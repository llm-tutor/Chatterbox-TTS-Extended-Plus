import os
import time
import random
import tempfile
import json
import csv
import gc
import re
import datetime
import string
import difflib
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import torch
import numpy as np
import torchaudio
import librosa
import soundfile as sf
from pydub import AudioSegment

# Enhanced monitoring
from monitoring import get_logger, record_operation_time

# Chatterbox imports
from chatterbox.src.chatterbox.tts import ChatterboxTTS
from chatterbox.src.chatterbox.vc import ChatterboxVC
# Project imports
from config import config_manager
from exceptions import ModelLoadError, GenerationError, AudioProcessingError, ResourceError, ValidationError

# Direct utils imports for better code visibility (Phase 4)
from utils.files.naming import generate_unique_filename, generate_enhanced_filename, sanitize_filename
from utils.files.operations import validate_audio_file
from utils.voice.metadata import update_voice_usage
from utils.outputs.management import save_generation_metadata
from utils.audio.processing import apply_speed_factor
from utils.audio.trimming import apply_audio_trimming
from utils.audio.post_processing import apply_complete_post_processing_pipeline

# Whisper imports
import whisper
from faster_whisper import WhisperModel as FasterWhisperModel
import nltk
from nltk.tokenize import sent_tokenize

logger = get_logger(__name__)

# ===== GLOBAL VARIABLES =====
_tts_model: Optional[ChatterboxTTS] = None
_vc_model: Optional[ChatterboxVC] = None
_whisper_model: Optional[Union[whisper.Whisper, FasterWhisperModel]] = None
_device: Optional[str] = None

def _get_device() -> str:
    """Get the optimal device for model loading"""
    global _device
    if _device is None:
        device_config = config_manager.get("models.device", "auto")
        
        if device_config == "auto":
            if torch.cuda.is_available():
                try:
                    # Test CUDA functionality
                    torch.zeros(1).cuda()
                    _device = "cuda"
                except Exception as e:
                    logger.warning(f"CUDA available but not functional: {e}")
                    _device = "cpu"
            else:
                _device = "cpu"
        else:
            _device = device_config
    
    return _device

def get_or_load_tts_model() -> ChatterboxTTS:
    """Load TTS model with enhanced error handling and timeout"""
    global _tts_model
    if _tts_model is None:
        from resilience import error_tracker, ErrorCategory, ErrorSeverity
        
        logger.info("TTS Model not loaded, initializing...")
        device = _get_device()
        
        try:
            # Model loading with timeout (for loading into memory, not downloading)
            loading_timeout = config_manager.get("error_handling.model_loading.loading_timeout_seconds", 300)
            
            if loading_timeout > 0:
                logger.info(f"Loading TTS model with {loading_timeout}s timeout...")
                
                # For now, load synchronously (timeout implementation would need threading)
                # In a future enhancement, we could add threading-based timeout
                start_time = time.time()
                _tts_model = ChatterboxTTS.from_pretrained(device)
                load_time = time.time() - start_time
                
                logger.info(f"TTS model loaded in {load_time:.1f}s")
                
                if load_time > loading_timeout:
                    logger.warning(f"TTS model loading took {load_time:.1f}s (longer than {loading_timeout}s timeout)")
            else:
                _tts_model = ChatterboxTTS.from_pretrained(device)
            
            if hasattr(_tts_model, 'to') and str(_tts_model.device) != device:
                _tts_model.to(device)
            
            logger.info(f"TTS Model loaded successfully on device: {getattr(_tts_model, 'device', 'unknown')}")
            
        except Exception as e:
            # Record the error
            error_tracker.record_error(
                operation="tts_model_loading",
                error=e,
                context={
                    'device': device,
                    'loading_timeout': loading_timeout,
                    'model_type': 'ChatterboxTTS'
                },
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
            
            logger.critical(f"Failed to load TTS model: {e}")
            
            # Check if we should shutdown on model failure
            shutdown_on_failure = config_manager.get("error_handling.model_loading.shutdown_on_failure", True)
            if shutdown_on_failure:
                logger.critical("Shutting down application due to TTS model loading failure")
                import sys
                sys.exit(1)
            else:
                raise ModelLoadError(f"TTS model loading failed: {e}")
                
    return _tts_model

def get_or_load_vc_model() -> ChatterboxVC:
    """Load VC model with enhanced error handling and timeout"""
    global _vc_model
    if _vc_model is None:
        from resilience import error_tracker, ErrorCategory, ErrorSeverity
        
        logger.info("VC Model not loaded, initializing...")
        device = _get_device()
        
        try:
            # Model loading with timeout
            loading_timeout = config_manager.get("error_handling.model_loading.loading_timeout_seconds", 300)
            
            if loading_timeout > 0:
                logger.info(f"Loading VC model with {loading_timeout}s timeout...")
                
                start_time = time.time()
                _vc_model = ChatterboxVC.from_pretrained(device)
                load_time = time.time() - start_time
                
                logger.info(f"VC model loaded in {load_time:.1f}s")
                
                if load_time > loading_timeout:
                    logger.warning(f"VC model loading took {load_time:.1f}s (longer than {loading_timeout}s timeout)")
            else:
                _vc_model = ChatterboxVC.from_pretrained(device)
            
            if hasattr(_vc_model, 'to') and str(_vc_model.device) != device:
                _vc_model.to(device)
            
            logger.info(f"VC Model loaded successfully on device: {getattr(_vc_model, 'device', 'unknown')}")
            
        except Exception as e:
            # Record the error
            error_tracker.record_error(
                operation="vc_model_loading",
                error=e,
                context={
                    'device': device,
                    'loading_timeout': loading_timeout,
                    'model_type': 'ChatterboxVC'
                },
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
            
            logger.critical(f"Failed to load VC model: {e}")
            
            # Check if we should shutdown on model failure
            shutdown_on_failure = config_manager.get("error_handling.model_loading.shutdown_on_failure", True)
            if shutdown_on_failure:
                logger.critical("Shutting down application due to VC model loading failure")
                import sys
                sys.exit(1)
            else:
                raise ModelLoadError(f"VC model loading failed: {e}")
                
    return _vc_model

def load_whisper_backend(model_name: str, use_faster_whisper: bool) -> Union[whisper.Whisper, FasterWhisperModel]:
    """Load Whisper model with specified backend"""
    device = _get_device()
    
    if use_faster_whisper:
        logger.info(f"Loading faster-whisper model: {model_name}")
        return FasterWhisperModel(
            model_name, 
            device=device, 
            compute_type="float16" if device == "cuda" else "float32"
        )
    else:
        logger.info(f"Loading openai-whisper model: {model_name}")
        return whisper.load_model(model_name, device=device)

def get_or_load_whisper_model() -> Union[whisper.Whisper, FasterWhisperModel]:
    """Load Whisper model with enhanced error handling"""
    global _whisper_model
    if _whisper_model is None:
        from resilience import error_tracker, ErrorCategory, ErrorSeverity
        
        logger.info("Whisper Model not loaded, initializing...")
        
        try:
            # Get whisper configuration
            model_name = config_manager.get("tts.whisper_model_name", "medium")
            use_faster_whisper = config_manager.get("tts.use_faster_whisper", True)
            
            # Model loading with timeout
            loading_timeout = config_manager.get("error_handling.model_loading.loading_timeout_seconds", 300)
            
            if loading_timeout > 0:
                logger.info(f"Loading Whisper model '{model_name}' (faster_whisper={use_faster_whisper}) with {loading_timeout}s timeout...")
                
                start_time = time.time()
                _whisper_model = load_whisper_backend(model_name, use_faster_whisper)
                load_time = time.time() - start_time
                
                logger.info(f"Whisper model loaded in {load_time:.1f}s")
                
                if load_time > loading_timeout:
                    logger.warning(f"Whisper model loading took {load_time:.1f}s (timeout: {loading_timeout}s)")
            else:
                _whisper_model = load_whisper_backend(model_name, use_faster_whisper)
                logger.info("Whisper model loaded (no timeout)")
            
        except Exception as e:
            # Record the error
            error_tracker.record_error(
                operation="whisper_model_loading",
                error=e,
                context={
                    'model_name': config_manager.get("tts.whisper_model_name", "medium"),
                    'use_faster_whisper': config_manager.get("tts.use_faster_whisper", True),
                    'loading_timeout': loading_timeout,
                    'device': _get_device()
                },
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
            
            logger.critical(f"Failed to load Whisper model: {e}")
            
            # Check if we should shutdown on model failure
            shutdown_on_failure = config_manager.get("error_handling.model_loading.shutdown_on_failure", True)
            if shutdown_on_failure:
                logger.critical("Shutting down application due to Whisper model loading failure")
                import sys
                sys.exit(1)
            else:
                raise ModelLoadError(f"Whisper model loading failed: {e}")
                
    return _whisper_model

def cleanup_whisper_model():
    """Clean up Whisper model to free VRAM"""
    global _whisper_model
    if _whisper_model is not None:
        logger.info("Cleaning up Whisper model...")
        try:
            # For faster-whisper, explicitly clean up
            if hasattr(_whisper_model, 'model'):
                del _whisper_model.model
            del _whisper_model
            _whisper_model = None
            
            # Force garbage collection and CUDA cleanup
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            logger.info("Whisper model cleanup completed")
        except Exception as e:
            logger.warning(f"Error during Whisper model cleanup: {e}")

def normalize_for_compare_all_punct(text: str) -> str:
    """Normalize text for comparison by removing punctuation and standardizing whitespace"""
    # Replace dashes with spaces
    text = re.sub(r'[–—-]', ' ', text)
    # Remove all punctuation
    text = re.sub(rf"[{re.escape(string.punctuation)}]", '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def whisper_check_mp(candidate_path: str, target_text: str, whisper_model: Union[whisper.Whisper, FasterWhisperModel], 
                    use_faster_whisper: bool) -> Tuple[str, float, str]:
    """
    Whisper validation function
    Returns: (candidate_path, score, transcribed_text)
    """
    try:
        logger.debug(f"Whisper checking: {candidate_path}")
        
        # Check if file exists and is not too small
        if not os.path.exists(candidate_path) or os.path.getsize(candidate_path) < 1024:
            logger.error(f"Candidate file missing or too small: {candidate_path}")
            return (candidate_path, 0.0, "ERROR: File missing or too small")
        
        # Transcribe using appropriate backend
        if use_faster_whisper:
            segments, info = whisper_model.transcribe(candidate_path)
            transcribed = "".join([seg.text for seg in segments]).strip().lower()
        else:
            result = whisper_model.transcribe(candidate_path)
            transcribed = result['text'].strip().lower()
        
        logger.debug(f"Whisper transcription: '{transcribed}' for candidate '{os.path.basename(candidate_path)}'")
        
        # Calculate similarity score using difflib
        score = difflib.SequenceMatcher(
            None,
            normalize_for_compare_all_punct(transcribed),
            normalize_for_compare_all_punct(target_text.strip().lower())
        ).ratio()
        
        logger.debug(f"Score: {score:.3f} (target: '{target_text}')")
        return (candidate_path, score, transcribed)
        
    except Exception as e:
        logger.error(f"Whisper transcription failed for {candidate_path}: {e}")
        return (candidate_path, 0.0, f"ERROR: {e}")

def set_seed(seed: int) -> int:
    """Set random seed for reproducibility, returns actual seed used"""
    if seed <= 0:
        seed = random.randint(1, 2**32 - 1)
    
    torch.manual_seed(seed)
    device = _get_device()
    if device == "cuda":
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)
    
    logger.debug(f"Seed set to: {seed}")
    return seed

# ===== HELPER FUNCTIONS =====

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    return re.sub(r'\s{2,}', ' ', text.strip())

def replace_letter_period_sequences(text: str) -> str:
    """Replace letter.period.sequences with spaced letters"""
    def replacer(match):
        cleaned = match.group(0).rstrip('.')
        letters = cleaned.split('.')
        return ' '.join(letters)
    
    pattern = r'\b[A-Za-z](?:\.[A-Za-z])*\.?'
    return re.sub(pattern, replacer, text)

def remove_inline_reference_numbers(text: str) -> str:
    """Remove reference numbers from text"""
    # Remove patterns like [1], [2], (1), (2), etc.
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\(\d+\)', '', text)
    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using NLTK"""
    try:
        # Download NLTK data if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        sentences = sent_tokenize(text)
        # Filter out very short sentences
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        return sentences
    except Exception as e:
        logger.warning(f"NLTK sentence splitting failed: {e}, using simple splitting")
        # Fallback to simple splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 3]

def group_sentences(sentences: List[str], max_chars: int = 400) -> List[List[str]]:
    """Group sentences into chunks with max character limit"""
    groups = []
    current_group = []
    current_chars = 0
    
    for sentence in sentences:
        sentence_chars = len(sentence)
        if current_chars + sentence_chars > max_chars and current_group:
            groups.append(current_group)
            current_group = [sentence]
            current_chars = sentence_chars
        else:
            current_group.append(sentence)
            current_chars += sentence_chars
    
    if current_group:
        groups.append(current_group)
    
    return groups

def smart_append_short_sentences(sentences: List[str], min_chars: int = 100) -> List[List[str]]:
    """Smart grouping of short sentences"""
    groups = []
    current_group = []
    current_chars = 0
    
    for sentence in sentences:
        sentence_chars = len(sentence)
        
        # If sentence is long enough on its own, make it its own group
        if sentence_chars >= min_chars:
            if current_group:
                groups.append(current_group)
                current_group = []
                current_chars = 0
            groups.append([sentence])
        else:
            # Add to current group
            current_group.append(sentence)
            current_chars += sentence_chars
            
            # If group is now long enough, finalize it
            if current_chars >= min_chars:
                groups.append(current_group)
                current_group = []
                current_chars = 0
    
    # Don't forget the last group
    if current_group:
        groups.append(current_group)
    
    return groups

# ===== SYNCHRONOUS CORE ENGINE CLASS =====

class CoreEngine:
    """Core engine matching Chatter.py performance patterns"""
    
    def __init__(self):
        self._temp_files = []  # Track temp files for cleanup
        
    def resolve_audio_path(self, source: str, context: str) -> Path:
        """
        Resolve audio file path based on context
        
        Args:
            source: filename, relative path, or URL
            context: 'tts_reference', 'vc_input', 'vc_target'
        """
        
        # Handle URLs - download to temp (synchronously)
        if source.startswith(('http://', 'https://')):
            temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / f"download_{int(time.time())}.wav"
            self._download_file_sync(source, temp_file)
            return temp_file
        
        # Handle absolute paths (like uploaded temp files)
        source_path = Path(source)
        if source_path.is_absolute() and source_path.exists():
            return source_path
        
        # Handle temp directory paths (uploaded files)
        if source.startswith('temp') or source.startswith('temp/') or source.startswith('temp\\'):
            # Convert relative temp path to absolute
            temp_path = Path(source)
            if temp_path.exists():
                return temp_path.resolve()  # Convert to absolute path
        
        # Determine base directory by context
        if context in ['tts_reference', 'vc_target']:
            base_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
        elif context == 'vc_input':
            base_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
        else:
            raise ValueError(f"Unknown context: {context}")
        
        # Try to find file with and without extensions
        search_paths = [
            base_dir / source,                          # exact path
            base_dir / f"{source}.wav",                 # add .wav
            base_dir / f"{source}.mp3",                 # add .mp3
            base_dir / f"{source}.flac",                # add .flac
        ]
        
        # Also search in subdirectories
        for subdir in base_dir.iterdir():
            if subdir.is_dir():
                search_paths.extend([
                    subdir / source,
                    subdir / f"{source}.wav",
                    subdir / f"{source}.mp3", 
                    subdir / f"{source}.flac",
                ])
        
        for path in search_paths:
            if path.exists():
                return path
        
        raise ResourceError(f"Audio file not found: {source} in {base_dir}")
    
    def _download_file_sync(self, url: str, destination: Path) -> None:
        """Download file synchronously with retry logic"""
        from resilience import retry_download, error_tracker, ErrorCategory, ErrorSeverity
        
        @retry_download(
            max_retries=config_manager.get("error_handling.download_retries.max_retries", 2),
            base_delay=config_manager.get("error_handling.download_retries.base_delay_seconds", 2.0),
            operation_name="file_download"
        )
        def _download_with_retry():
            import requests
            timeout = config_manager.get("api.download_timeout_seconds", 30)
            
            logger.info(f"Downloading {url} to {destination}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(response.content)
            
            self._temp_files.append(destination)  # Track for cleanup
            logger.info(f"Successfully downloaded {url} to {destination}")
            
        try:
            _download_with_retry()
        except Exception as e:
            # Enhanced error logging with context
            error_tracker.record_error(
                operation="file_download",
                error=e,
                context={
                    'url': url,
                    'destination': str(destination),
                    'timeout': config_manager.get("api.download_timeout_seconds", 30)
                },
                category=ErrorCategory.TRANSIENT,  # Downloads are typically transient failures
                severity=ErrorSeverity.HIGH
            )
            logger.error(f"Download failed after retries: {url} -> {e}")
            raise AudioProcessingError(f"Download failed after retries: {e}")
    
    def convert_audio_formats(self, wav_path: Path, formats: List[str]) -> List[Dict[str, str]]:
        """Convert WAV to additional formats with project folder support"""
        output_files = []
        base_name = Path(wav_path).stem
        output_dir = Path(wav_path).parent
        
        # Determine relative path from outputs directory for URL generation
        base_outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        try:
            relative_path = output_dir.relative_to(base_outputs_dir)
            # Convert to forward slashes for URLs (works on all platforms)
            relative_path_str = str(relative_path).replace('\\', '/')
            url_prefix = f"/outputs/{relative_path_str}/" if relative_path != Path('.') else "/outputs/"
        except ValueError:
            # Fallback if output_dir is not under base_outputs_dir
            url_prefix = "/outputs/"
        
        for fmt in formats:
            fmt_lower = fmt.lower()
            if fmt_lower == 'wav':
                output_files.append({
                    'format': 'wav',
                    'filename': Path(wav_path).name,
                    'url': f'{url_prefix}{Path(wav_path).name}',
                    'path': str(wav_path)
                })
            else:
                try:
                    audio = AudioSegment.from_wav(str(wav_path))
                    output_path = output_dir / f"{base_name}.{fmt_lower}"
                    
                    # Use the same approach as Chatter.py
                    if fmt_lower == 'mp3':
                        audio.export(str(output_path), format=fmt_lower, bitrate='320k')
                    else:
                        # For FLAC and other formats, use simple export without extra parameters
                        audio.export(str(output_path), format=fmt_lower)
                    
                    output_files.append({
                        'format': fmt_lower,
                        'filename': output_path.name,
                        'url': f'{url_prefix}{output_path.name}',
                        'path': str(output_path)
                    })
                    
                    logger.debug(f"Converted to {fmt}: {output_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to convert to {fmt}: {e}")
                    logger.error(f"Conversion error details: {type(e).__name__}: {str(e)}")
                    # Continue with other formats
        
        return output_files
    
    def process_text_preprocessing(self, text: str, **kwargs) -> str:
        """Preprocess text applying all text parameters"""
        
        # 1. Sound word replacement/removal (NEW feature)
        sound_words_field = kwargs.get('sound_words_field', '')
        if sound_words_field and sound_words_field.strip():
            sound_words = self.parse_sound_word_field(sound_words_field)
            if sound_words:
                text = self.smart_remove_sound_words(text, sound_words)
        
        # 2. Case normalization
        if kwargs.get('to_lowercase', True):
            text = text.lower()
        
        # 3. Whitespace normalization  
        if kwargs.get('normalize_spacing', True):
            text = normalize_whitespace(text)
        
        # 4. Letter-period sequence fixes (e.g., "U.S.A." → "U S A")
        if kwargs.get('fix_dot_letters', True):
            text = replace_letter_period_sequences(text)
        
        # 5. Reference number removal (academic citations)
        if kwargs.get('remove_reference_numbers', True):
            text = remove_inline_reference_numbers(text)
        
        return text

    def parse_sound_word_field(self, user_input: str) -> List[Tuple[str, str]]:
        """Parse sound word field from user input"""
        lines = [l.strip() for l in user_input.replace(',', '\n').split('\n') if l.strip()]
        result = []
        for line in lines:
            if '=>' in line:
                pattern, replacement = line.split('=>', 1)
                result.append((pattern.strip(), replacement.strip()))
            else:
                result.append((line, ''))  # Remove (replace with empty string)
        return result

    def smart_remove_sound_words(self, text: str, sound_words: List[Tuple[str, str]]) -> str:
        """Smart sound word replacement"""
        for pattern, replacement in sound_words:
            if replacement:
                # 1. Handle possessive: "Baggins’" or "Baggins'" (optionally with s or S after apostrophe)
                text = re.sub(
                    r'(?i)(%s)([’\']s?)' % re.escape(pattern),
                    lambda m: replacement + "'s" if m.group(2) else replacement,
                    text
                )
                # 2. Replace word in quotes
                text = re.sub(
                    r'(["\'])%s(["\'])' % re.escape(pattern),
                    lambda m: f"{m.group(1)}{replacement}{m.group(2)}",
                    text,
                    flags=re.IGNORECASE
                )
                # 3. Replace as whole word (not in quotes)
                text = re.sub(
                    r'\b%s\b' % re.escape(pattern),
                    replacement,
                    text,
                    flags=re.IGNORECASE
                )
            else:
                # Remove word plus adjacent punctuation/spaces/quotes
                text = re.sub(
                    r'([\'"]?)(,? ?){0,1}%s(,? ?){0,1}([\'"]?)' % re.escape(pattern),
                    '',
                    text,
                    flags=re.IGNORECASE
                )
                text = re.sub(
                    r'(,? ?){0,1}\b%s\b(,? ?){0,1}' % re.escape(pattern),
                    '',
                    text,
                    flags=re.IGNORECASE
                )
        # Clean up doubled-up commas and extra spaces
        text = re.sub(r'([,\s]+,)+', ',', text)
        text = re.sub(r',\s*,+', ',', text)
        text = re.sub(r'\s{2,}', ' ', text)
        text = re.sub(r'(\s+,|,\s+)', ', ', text)
        text = re.sub(r'(^|[\.!\?]\s*),+', r'\1', text)
        text = re.sub(r',+\s*([\.!\?])', r'\1', text)
        return text.strip()

    def process_one_chunk(self, model, sentence_group: str, idx: int, gen_index: int, this_seed: int,
                         audio_prompt_path_input: Optional[str], exaggeration_input: float, 
                         temperature_input: float, cfgw_input: float, disable_watermark: bool,
                         num_candidates_per_chunk: int, max_attempts_per_candidate: int,
                         bypass_whisper_checking: bool, retry_attempt_number: int = 1) -> Tuple[int, List[str]]:
        """
        Process one chunk of text
        """
        candidates = []
        try:
            if not sentence_group.strip():
                logger.debug(f"Skipping empty sentence group at index {idx}")
                return (idx, candidates)
            if len(sentence_group) > 500:
                logger.debug(f"Skipping suspiciously long sentence group at index {idx} (len={len(sentence_group)})")
                return (idx, candidates)
            
            logger.debug(f"Processing group {idx}: len={len(sentence_group)}: {sentence_group}")

            for cand_idx in range(num_candidates_per_chunk):
                for attempt in range(max_attempts_per_candidate):
                    if cand_idx == 0 and attempt == 0:
                        candidate_seed = this_seed
                    else:
                        candidate_seed = random.randint(1, 2**32-1)
                    set_seed(candidate_seed)
                    try:
                        logger.debug(f"Generating candidate {cand_idx+1} attempt {attempt+1} for chunk {idx}...")
                        
                        # This is the critical call to chatterbox model
                        wav = model.generate(
                            sentence_group,
                            audio_prompt_path=audio_prompt_path_input,
                            exaggeration=min(exaggeration_input, 1.0),
                            temperature=temperature_input,
                            cfg_weight=cfgw_input,
                            apply_watermark=not disable_watermark
                        )
                        
                        # Save candidate
                        temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
                        candidate_path = temp_dir / f"gen{gen_index+1}_chunk_{idx:03d}_cand_{cand_idx+1}_try{retry_attempt_number}_seed{candidate_seed}.wav"
                        torchaudio.save(str(candidate_path), wav, model.sr)
                        
                        # Wait for file to be written (like original)
                        for _ in range(10):
                            if os.path.exists(candidate_path) and os.path.getsize(candidate_path) > 1024:
                                break
                            time.sleep(0.1)
                        else:
                            logger.warning(f"File {candidate_path} was not created or is too small")
                            continue
                        
                        logger.debug(f"Saved candidate {cand_idx+1}, attempt {attempt+1}, duration={librosa.get_duration(filename=str(candidate_path)):.3f}s: {candidate_path}")
                        # TO-FIX: Consider if we are losing useful information here (Chatter.py:537)
                        candidates.append(str(candidate_path))
                        break  # Success, move to next candidate
                        
                    except Exception as e:
                        logger.error(f"Failed to generate candidate {cand_idx+1} attempt {attempt+1} for chunk {idx}: {e}")
                        continue
            
            return idx, candidates
            
        except Exception as e:
            logger.error(f"Error processing chunk {idx}: {e}")
            return idx, []

    def generate_tts(self, **kwargs) -> Dict:
        """
        Generate TTS audio
        Returns dictionary with output_files, seed_used, processing_time, etc.
        """
        start_time = time.time()
        
        with logger.operation_timer("tts_generation", record_metrics=True):
            try:
                # Load model
                model = get_or_load_tts_model()
                
                # Extract and validate parameters
                text = kwargs.get('text', '').strip()
                if not text:
                    raise ValidationError("Text cannot be empty")
                
                # Validate text length
                max_length = config_manager.get("api.max_text_length", 10000)
                if len(text) > max_length:
                    raise ValidationError(f"Text too long. Maximum length: {max_length} characters")
                
                logger.info("Starting TTS generation",
                           extra_data={'text_length': len(text), 'parameters': {k: v for k, v in kwargs.items() if k != 'text'}})
                
                # Handle seed
                seed = kwargs.get('seed', 0)
                actual_seed = set_seed(seed)
                
                # Handle reference audio
                ref_audio_path = None
                if kwargs.get('reference_audio_filename'):
                    ref_audio_path = self.resolve_audio_path(
                        kwargs['reference_audio_filename'], 
                        'tts_reference'
                    )
                    logger.info(f"Using reference audio: {ref_audio_path}")
                    
                    # Update voice usage statistics
                    try:
                        update_voice_usage(ref_audio_path)
                    except Exception as e:
                        logger.warning(f"Failed to update voice usage: {e}")
                
                # Process text with preprocessing options (exclude 'text' from kwargs to avoid duplicate)
                preprocessing_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
                processed_text = self.process_text_preprocessing(text, **preprocessing_kwargs)
                
                # Call the TTS generation logic (exclude 'text' from kwargs)
                generation_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
                # We generate the final wav file, including post-processing
                wav_output_path = self._process_tts_generation_sync(processed_text, ref_audio_path, **generation_kwargs)
                
                # Convert to requested formats
                export_formats = kwargs.get('export_formats', ['wav', 'mp3'])
                output_files = self.convert_audio_formats(wav_output_path, export_formats)
                
                processing_time = time.time() - start_time
                
                # Save generation metadata
                metadata = {
                    'type': 'tts',
                    'parameters': {
                        'text': text,
                        'reference_audio_filename': kwargs.get('reference_audio_filename'),
                        'temperature': kwargs.get('temperature', 0.75),
                        'seed': actual_seed,
                        'exaggeration': kwargs.get('exaggeration', 0.5),
                        'speed_factor': kwargs.get('speed_factor', 1.0),
                        'trim': kwargs.get('trim', False),
                        'trim_threshold_ms': kwargs.get('trim_threshold_ms', 200),
                        'cfg_weight': kwargs.get('cfg_weight', 1.0),
                        'num_candidates_per_chunk': kwargs.get('num_candidates_per_chunk', 3),
                        'max_attempts_per_candidate': kwargs.get('max_attempts_per_candidate', 3),
                        'bypass_whisper_checking': kwargs.get('bypass_whisper_checking', False),
                        'whisper_model_name': kwargs.get('whisper_model_name', 'medium'),
                        'use_faster_whisper': kwargs.get('use_faster_whisper', True),
                        'enable_batching': kwargs.get('enable_batching', False),
                        'export_formats': export_formats
                    },
                    'generation_info': {
                        'processing_time_seconds': processing_time,
                        'seed_used': actual_seed,
                        'chunks_processed': 1,  # We'll track this properly later
                        'text_length': len(text),
                        'processed_text_length': len(processed_text)
                    },
                    'files': {file['format']: file['filename'] for file in output_files}
                }
                
                # Save metadata using utility function
                if output_files:
                    save_generation_metadata(output_files[0]['filename'], metadata)
                
                return {
                    'success': True,
                    'output_files': output_files,
                    'generation_seed_used': actual_seed,
                    'processing_time_seconds': processing_time,
                    'message': 'TTS generation completed successfully'
                }
                
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")
                if isinstance(e, (ValidationError, ResourceError, ModelLoadError)):
                    raise
                else:
                    raise GenerationError(f"TTS generation failed: {e}")

    def _process_tts_generation_sync(self, text: str, ref_audio_path: Optional[Path], **kwargs) -> Path:
        """
        TTS generation with chunking, retry, and Whisper validation
        This is the performance-critical method
        """
        try:
            model = get_or_load_tts_model()
            
            # Prepare output directory with project folder support
            base_output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            
            # Handle project folder parameter
            project_folder = kwargs.get('project')
            if project_folder:
                output_dir = base_output_dir / project_folder
                logger.info(f"Using project folder: {project_folder}")
            else:
                output_dir = base_output_dir
                
            output_dir.mkdir(parents=True, exist_ok=True)
            temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
            temp_dir.mkdir(exist_ok=True)

            # Clean temp directory
            for f in temp_dir.iterdir():
                if f.is_file():
                    f.unlink()

            # Extract parameters with defaults
            num_generations = kwargs.get('num_generations', 1)
            enable_batching = kwargs.get('enable_batching', False)
            smart_batch_short_sentences = kwargs.get('smart_batch_short_sentences', True)
            num_candidates_per_chunk = kwargs.get('num_candidates_per_chunk', 3)
            max_attempts_per_candidate = kwargs.get('max_attempts_per_candidate', 3)
            bypass_whisper_checking = kwargs.get('bypass_whisper_checking', False)
            whisper_model_name = kwargs.get('whisper_model_name', 'medium')
            use_faster_whisper = kwargs.get('use_faster_whisper', True)
            use_longest_transcript_on_fail = kwargs.get('use_longest_transcript_on_fail', True)

            # TTS generation parameters
            exaggeration = kwargs.get('exaggeration', config_manager.get("tts_defaults.exaggeration", 0.5))
            temperature = kwargs.get('temperature', config_manager.get("tts_defaults.temperature", 0.75))
            cfg_weight = kwargs.get('cfg_weight', config_manager.get("tts_defaults.cfg_weight", 1.0))
            disable_watermark = kwargs.get('disable_watermark', config_manager.get("tts_defaults.disable_watermark", True))
            
            # Split text into sentences
            sentences = split_into_sentences(text)
            logger.info(f"Split text into {len(sentences)} sentences")
            
            # Group sentences based on batching settings
            if enable_batching:
                sentence_groups = group_sentences(sentences, max_chars=400)
            elif smart_batch_short_sentences:
                sentence_groups = smart_append_short_sentences(sentences)
            else:
                sentence_groups = [[s] for s in sentences]  # Each sentence is its own group
            
            logger.info(f"Created {len(sentence_groups)} sentence groups")
            
            # Extract parallel processing parameters
            enable_parallel = kwargs.get('enable_parallel', config_manager.get("tts_defaults.enable_parallel", True))
            num_parallel_workers = kwargs.get('num_parallel_workers', config_manager.get("tts_defaults.num_parallel_workers", 4))
            
            # Process each sentence group - PARALLEL or SEQUENTIAL based on settings
            all_candidates = {}
            audio_prompt_path_str = str(ref_audio_path) if ref_audio_path else None
            
            for gen_index in range(num_generations):
                logger.info(f"Starting generation {gen_index + 1}/{num_generations}")
                generation_seed = random.randint(1, 2**32-1)
                
                if enable_parallel and len(sentence_groups) > 1:
                    # Parallel processing with ThreadPoolExecutor
                    logger.info(f"Processing {len(sentence_groups)} chunks in parallel with {num_parallel_workers} workers")
                    
                    with ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
                        # Submit all chunks for parallel processing
                        futures = []
                        for group_idx, sentence_group in enumerate(sentence_groups):
                            sentence_text = ' '.join(sentence_group)
                            future = executor.submit(
                                self.process_one_chunk,
                                model, sentence_text, group_idx, gen_index, generation_seed,
                                audio_prompt_path_str, exaggeration, temperature, cfg_weight,
                                disable_watermark, num_candidates_per_chunk, max_attempts_per_candidate,
                                bypass_whisper_checking, retry_attempt_number=1
                            )
                            futures.append(future)
                        
                        # Collect results with progress tracking
                        completed = 0
                        total_chunks = len(futures)
                        for future in as_completed(futures):
                            try:
                                chunk_idx, candidates = future.result()
                                if candidates:
                                    all_candidates[f"gen_{gen_index}_chunk_{chunk_idx}"] = candidates
                                    logger.debug(f"Generation {gen_index}, chunk {chunk_idx}: {len(candidates)} candidates")
                                else:
                                    logger.warning(f"No candidates generated for generation {gen_index}, chunk {chunk_idx}")
                                
                                completed += 1
                                percent = int(100 * completed / total_chunks)
                                logger.info(f"[PROGRESS] Generated chunk {completed}/{total_chunks} ({percent}%)")
                                
                            except Exception as e:
                                logger.error(f"Error processing chunk in parallel: {e}")
                else:
                    # Sequential processing (fallback or single chunk)
                    logger.info(f"Processing {len(sentence_groups)} chunks sequentially")
                    
                    for group_idx, sentence_group in enumerate(sentence_groups):
                        sentence_text = ' '.join(sentence_group)
                        
                        # Process this chunk
                        chunk_idx, candidates = self.process_one_chunk(
                            model, sentence_text, group_idx, gen_index, generation_seed,
                            audio_prompt_path_str, exaggeration, temperature, cfg_weight,
                            disable_watermark, num_candidates_per_chunk, max_attempts_per_candidate,
                            bypass_whisper_checking, retry_attempt_number=1
                        )
                        
                        if candidates:
                            all_candidates[f"gen_{gen_index}_chunk_{chunk_idx}"] = candidates
                            logger.debug(f"Generation {gen_index}, chunk {chunk_idx}: {len(candidates)} candidates")
                        else:
                            logger.warning(f"No candidates generated for generation {gen_index}, chunk {chunk_idx}")
            
            if not all_candidates:
                raise GenerationError("No audio candidates were generated successfully")
            
            # Select best candidates and combine - WITH WHISPER VALIDATION
            logger.info("Validating candidates with Whisper and selecting best...")
            
            # Load Whisper model for validation if not bypassed
            whisper_model = None
            if not bypass_whisper_checking:
                whisper_model = get_or_load_whisper_model()
            
            # Process each generation with full validation pipeline
            final_chunks = []
            for gen_index in range(num_generations):
                logger.info(f"Processing generation {gen_index + 1}/{num_generations}")
                
                # Create chunk candidate map
                chunk_candidate_map = {}
                for group_idx in range(len(sentence_groups)):
                    key = f"gen_{gen_index}_chunk_{group_idx}"
                    if key in all_candidates and all_candidates[key]:
                        chunk_candidate_map[group_idx] = []
                        for candidate_path in all_candidates[key]:
                            try:
                                duration = librosa.get_duration(filename=candidate_path)
                                chunk_candidate_map[group_idx].append({
                                    'path': candidate_path,
                                    'duration': duration,
                                    'sentence_group': ' '.join(sentence_groups[group_idx])
                                })
                            except Exception as e:
                                logger.warning(f"Could not get duration for {candidate_path}: {e}")
                
                if not chunk_candidate_map:
                    continue
                
                # Get selected candidates using validation
                selected_candidates = self._validate_and_select_candidates(
                    chunk_candidate_map, sentence_groups, whisper_model, use_faster_whisper,
                    bypass_whisper_checking, use_longest_transcript_on_fail, max_attempts_per_candidate,
                    model, audio_prompt_path_str, exaggeration, temperature, cfg_weight,
                    disable_watermark, num_candidates_per_chunk, enable_parallel, num_parallel_workers, gen_index
                )
                
                if selected_candidates:
                    # Phase 10.1.2 Optimization: Separate speed factor processing
                    # Step 1: Combine chunks (always at 1.0x speed)
                    combined_path = self._combine_audio_chunks(selected_candidates, gen_index, kwargs)
                    
                    # Step 2: Apply speed factor as post-processing if needed
                    speed_factor = kwargs.get('speed_factor', 1.0)
                    if abs(speed_factor - 1.0) >= 1e-6:
                        combined_path = self.apply_speed_factor_post_processing(combined_path, speed_factor, kwargs)
                    
                    # Step 3: Apply trimming as post-processing if requested
                    trim_enabled = kwargs.get('trim', False)
                    if trim_enabled:
                        combined_path = self._apply_trimming_post_processing(combined_path, kwargs)
                    
                    final_chunks.append(combined_path)
            
            if not final_chunks:
                raise GenerationError("No final audio chunks were created")

            # Apply post-processing pipeline to the final output (auto-editor + ffmpeg normalization)
            # Process final_chunks[0] which contains the complete generated audio
            logger.info("🎨 Applying post-processing pipeline...")
            final_audio_path = apply_complete_post_processing_pipeline(final_chunks[0], kwargs)
            
            # Return the final processed audio
            return Path(final_audio_path)
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise GenerationError(f"TTS generation failed: {e}")

    def _validate_and_select_candidates(self, chunk_candidate_map: Dict, sentence_groups: List, 
                                      whisper_model, use_faster_whisper: bool, bypass_whisper_checking: bool,
                                      use_longest_transcript_on_fail: bool, max_attempts_per_candidate: int,
                                      model, audio_prompt_path_str: Optional[str], exaggeration: float, temperature: float,
                                      cfg_weight: float, disable_watermark: bool, num_candidates_per_chunk: int,
                                      enable_parallel: bool, num_parallel_workers: int, gen_index: int) -> List[str]:
        """
        Validate candidates with Whisper and select best ones
        Returns list of selected candidate paths in chunk order
        """
        # Initialize validation tracking
        chunk_validations = {chunk_idx: [] for chunk_idx in chunk_candidate_map.keys()}
        chunk_failed_candidates = {chunk_idx: [] for chunk_idx in chunk_candidate_map.keys()}
        
        if bypass_whisper_checking:
            logger.info("Bypassing Whisper validation - selecting shortest duration candidates")
            selected_candidates = []
            for chunk_idx in sorted(chunk_candidate_map.keys()):
                candidates = chunk_candidate_map[chunk_idx]
                if candidates:
                    shortest = min(candidates, key=lambda c: c['duration'])
                    selected_candidates.append(shortest['path'])
                    logger.info(f"[Chunk {chunk_idx}] Selected shortest candidate: {os.path.basename(shortest['path'])} (BYPASS MODE)")
            return selected_candidates
        
        # Full Whisper validation
        logger.info(f"Running Whisper validation on {sum(len(candidates) for candidates in chunk_candidate_map.values())} candidates")
        logger.info(f"Validation criteria: score >= 0.95 threshold, model: {whisper_model.__class__.__name__}")
        logger.info(f"Retry configuration: max_attempts_per_candidate={max_attempts_per_candidate}")
        
        validation_start_time = time.time()
        for chunk_idx, candidates in chunk_candidate_map.items():
            sentence_group = candidates[0]['sentence_group'] if candidates else ""
            logger.debug(f"[Chunk {chunk_idx}] Validating {len(candidates)} candidates for text: '{sentence_group[:50]}{'...' if len(sentence_group) > 50 else ''}'")
            
            for cand in candidates:
                candidate_path = cand['path']
                try:
                    path, score, transcribed = whisper_check_mp(candidate_path, sentence_group, whisper_model, use_faster_whisper)
                    logger.debug(f"[Chunk {chunk_idx}] {os.path.basename(candidate_path)}: score={score:.3f}, transcript='{transcribed[:30]}{'...' if len(transcribed) > 30 else ''}'")
                    
                    if score >= 0.95:
                        chunk_validations[chunk_idx].append((cand['duration'], cand['path']))
                        logger.debug(f"[Chunk {chunk_idx}] ✅ PASSED validation: {os.path.basename(candidate_path)}")
                    else:
                        chunk_failed_candidates[chunk_idx].append((score, cand['path'], transcribed))
                        logger.debug(f"[Chunk {chunk_idx}] ❌ FAILED validation: {os.path.basename(candidate_path)} (score={score:.3f} < 0.95)")
                        
                except Exception as e:
                    logger.error(f"Whisper validation failed for {candidate_path}: {e}")
                    chunk_failed_candidates[chunk_idx].append((0.0, candidate_path, ""))
        
        validation_time = time.time() - validation_start_time
        logger.info(f"Initial validation completed in {validation_time:.1f}s")
        
        # FULL RETRY QUEUE IMPLEMENTATION
        retry_queue = [chunk_idx for chunk_idx in chunk_candidate_map.keys() if not chunk_validations[chunk_idx]]
        chunk_attempts = {chunk_idx: 1 for chunk_idx in chunk_candidate_map.keys()}  # Track attempts per chunk
        
        passed_chunks = len([idx for idx in chunk_candidate_map.keys() if chunk_validations[idx]])
        failed_chunks = len(retry_queue)
        logger.info(f"Initial validation summary: {passed_chunks} chunks PASSED, {failed_chunks} chunks FAILED")
        
        if retry_queue:
            logger.warning(f"Failed chunks needing retry: {retry_queue}")
        else:
            logger.info("✅ All chunks passed initial validation - no retry needed")
        
        retry_attempt = 0
        while retry_queue:
            retry_attempt += 1
            # Filter retry queue to only chunks that haven't exceeded max attempts
            still_need_retry = [
                chunk_idx for chunk_idx in retry_queue 
                if chunk_attempts[chunk_idx] < max_attempts_per_candidate
            ]
            if not still_need_retry:
                logger.warning(f"🛑 All failed chunks reached max retry attempts ({max_attempts_per_candidate})")
                break
            
            logger.warning(f"🔄 RETRY ATTEMPT {retry_attempt}: Processing {len(still_need_retry)} chunks (attempt {chunk_attempts[still_need_retry[0]]+1}/{max_attempts_per_candidate})")
            
            # Generate new candidates for failed chunks
            retry_candidate_map = {}
            retry_start_time = time.time()
            if enable_parallel and len(still_need_retry) > 1:
                # Parallel retry processing
                logger.info(f"🔄 Parallel retry with {num_parallel_workers} workers")
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
                    futures = []
                    for chunk_idx in still_need_retry:
                        sentence_group = sentence_groups[chunk_idx]
                        # Generate new seed for retry
                        retry_seed = random.randint(0, 999999999)
                        logger.debug(f"🔄 [Chunk {chunk_idx}] Retry seed: {retry_seed}")
                        
                        future = executor.submit(
                            self.process_one_chunk,
                            model, sentence_group, chunk_idx, gen_index, retry_seed,
                            audio_prompt_path_str, exaggeration, temperature, cfg_weight,
                            disable_watermark, 1, max_attempts_per_candidate,  # Only 1 candidate for retry
                            f"retry_gen_{gen_index}_chunk_{chunk_idx}_attempt_{chunk_attempts[chunk_idx]+1}"
                        )
                        futures.append((chunk_idx, future))
                    
                    # Collect retry results
                    for chunk_idx, future in futures:
                        try:
                            result_chunk_idx, candidates = future.result()
                            if candidates:
                                retry_candidate_map[chunk_idx] = candidates
                                logger.info(f"🔄 [Chunk {chunk_idx}] Generated {len(candidates)} retry candidates")
                        except Exception as e:
                            logger.error(f"🔄 [Chunk {chunk_idx}] Retry generation failed: {e}")
            else:
                # Sequential retry processing
                logger.info(f"🔄 Sequential retry processing")
                for chunk_idx in still_need_retry:
                    sentence_group = sentence_groups[chunk_idx]
                    # Generate new seed for retry
                    retry_seed = random.randint(0, 999999999)
                    logger.debug(f"🔄 [Chunk {chunk_idx}] Retry seed: {retry_seed}")
                    
                    try:
                        result_chunk_idx, candidates = self.process_one_chunk(
                            model, sentence_group, chunk_idx, gen_index, retry_seed,
                            audio_prompt_path_str, exaggeration, temperature, cfg_weight,
                            disable_watermark, 1, max_attempts_per_candidate,  # Only 1 candidate for retry
                            f"retry_gen_{gen_index}_chunk_{chunk_idx}_attempt_{chunk_attempts[chunk_idx]+1}"
                        )
                        if candidates:
                            retry_candidate_map[chunk_idx] = candidates
                            logger.info(f"🔄 [Chunk {chunk_idx}] Generated {len(candidates)} retry candidates")
                    except Exception as e:
                        logger.error(f"🔄 [Chunk {chunk_idx}] Retry generation failed: {e}")
            
            retry_gen_time = time.time() - retry_start_time
            logger.info(f"🔄 Retry generation completed in {retry_gen_time:.1f}s")
            
            # Validate retry candidates
            retry_validation_start = time.time()
            for chunk_idx, candidates in retry_candidate_map.items():
                sentence_group = sentence_groups[chunk_idx]
                logger.debug(f"🔄 [Chunk {chunk_idx}] Validating {len(candidates)} retry candidates")
                
                for candidate_path in candidates:
                    try:
                        path, score, transcribed = whisper_check_mp(candidate_path, sentence_group, whisper_model, use_faster_whisper)
                        duration = librosa.get_duration(filename=candidate_path)
                        logger.debug(f"🔄 [Chunk {chunk_idx}] RETRY {os.path.basename(candidate_path)}: score={score:.3f}")
                        
                        if score >= 0.95:
                            chunk_validations[chunk_idx].append((duration, candidate_path))
                            logger.info(f"🔄 [Chunk {chunk_idx}] ✅ RETRY SUCCESS: {os.path.basename(candidate_path)} (score={score:.3f})")
                        else:
                            chunk_failed_candidates[chunk_idx].append((score, candidate_path, transcribed))
                            logger.debug(f"🔄 [Chunk {chunk_idx}] ❌ RETRY FAILED: {os.path.basename(candidate_path)} (score={score:.3f})")
                            
                    except Exception as e:
                        logger.error(f"Whisper validation failed for retry {candidate_path}: {e}")
                        chunk_failed_candidates[chunk_idx].append((0.0, candidate_path, ""))
            
            retry_validation_time = time.time() - retry_validation_start
            logger.info(f"🔄 Retry validation completed in {retry_validation_time:.1f}s")
            
            # Update retry queue and attempt counts
            retry_queue = [chunk_idx for chunk_idx in still_need_retry if not chunk_validations[chunk_idx]]
            for chunk_idx in still_need_retry:
                chunk_attempts[chunk_idx] += 1
            
            if retry_queue:
                logger.warning(f"🔄 Still need retry: {retry_queue} (attempts: {[chunk_attempts[idx] for idx in retry_queue]})")
            else:
                logger.info(f"🔄 ✅ All chunks now have valid candidates after retry attempt {retry_attempt}")
        
        total_validation_time = time.time() - validation_start_time
        logger.info(f"🏁 Complete validation finished in {total_validation_time:.1f}s (including {retry_attempt} retry attempts)")
        
        # Final candidate selection
        selected_candidates = []
        logger.info("🎯 Final candidate selection:")
        for chunk_idx in sorted(chunk_candidate_map.keys()):
            if chunk_validations[chunk_idx]:
                # Best passed candidate (shortest duration)
                best = min(chunk_validations[chunk_idx], key=lambda x: x[0])
                selected_candidates.append(best[1])
                logger.info(f"[Chunk {chunk_idx}] ✅ Selected validated candidate: {os.path.basename(best[1])} (duration={best[0]:.2f}s, PASSED Whisper)")
            elif chunk_failed_candidates[chunk_idx]:
                # Fallback strategies
                failed = chunk_failed_candidates[chunk_idx]
                if use_longest_transcript_on_fail:
                    # Select candidate with longest transcript
                    best = max(failed, key=lambda x: len(x[2]))
                    strategy = "longest transcript"
                else:
                    # Select candidate with highest score
                    best = max(failed, key=lambda x: x[0])
                    strategy = "highest score"
                selected_candidates.append(best[1])
                logger.warning(f"[Chunk {chunk_idx}] ⚠️ FALLBACK ({strategy}): {os.path.basename(best[1])} (score={best[0]:.3f}, transcript='{best[2][:30]}{'...' if len(best[2]) > 30 else ''}')")
            else:
                logger.error(f"[Chunk {chunk_idx}] ❌ No candidates available")
                return []
        
        logger.info(f"🏁 Final selection: {len(selected_candidates)} chunks ready for assembly")
        return selected_candidates

    def _combine_audio_chunks(self, chunk_paths: List[str], gen_index: int, generation_params: Dict[str, Any] = None) -> str:
        """
        Combine audio chunks into a single file
        
        Phase 10.1.2 Optimization: Speed factor processing moved to separate method
        This eliminates overhead for speed_factor=1.0 (most common case)
        """
        try:
            # Use same output directory logic as main generation (with project folder support)
            base_output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            project_folder = generation_params.get('project')
            if project_folder:
                output_dir = base_output_dir / project_folder
            else:
                output_dir = base_output_dir
            
            # Use enhanced filename generation (excluding speed_factor for base file)
            params = generation_params or {}
            # Create base filename without speed_factor
            base_params = {k: v for k, v in params.items() if k != 'speed_factor'}
            filename = generate_enhanced_filename("tts", base_params, "wav")
            output_path = output_dir / filename
            
            if len(chunk_paths) == 1:
                # Single chunk - just copy it
                import shutil
                shutil.copy2(chunk_paths[0], output_path)
                logger.info(f"Single chunk copied to: {output_path}")
            else:
                # Multiple chunks - combine them
                combined_audio = None
                sample_rate = None
                
                for chunk_path in chunk_paths:
                    audio, sr = torchaudio.load(chunk_path)
                    if combined_audio is None:
                        combined_audio = audio
                        sample_rate = sr
                    else:
                        # Ensure same sample rate
                        if sr != sample_rate:
                            audio = torchaudio.functional.resample(audio, sr, sample_rate)
                        combined_audio = torch.cat([combined_audio, audio], dim=1)
                
                torchaudio.save(str(output_path), combined_audio, sample_rate)
                logger.info(f"Combined {len(chunk_paths)} chunks to: {output_path}")
            
            # OPTIMIZATION: Return base file path without speed factor processing
            # Speed factor will be applied separately if needed
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to combine audio chunks: {e}")
            raise AudioProcessingError(f"Audio combination failed: {e}")

    def apply_speed_factor_post_processing(self, audio_path: str, speed_factor: float, generation_params: Dict[str, Any] = None) -> str:
        """
        Apply speed factor as post-processing step (Phase 10.1.2 optimization)
        
        This method is called separately after generation to apply speed factor,
        eliminating overhead for speed_factor=1.0 cases.
        """
        if abs(speed_factor - 1.0) < 1e-6:
            # No processing needed for 1.0x speed
            return audio_path
        
        try:
            logger.info(f"Applying speed factor {speed_factor}x as post-processing")
            
            # Load the audio
            audio_tensor, sample_rate = torchaudio.load(audio_path)
            
            # Apply speed factor using optimized utils function
            speed_factor_library = generation_params.get('speed_factor_library', 'auto')
            processed_audio = apply_speed_factor(
                audio_tensor, 
                sample_rate, 
                speed_factor,
                preferred_library=speed_factor_library
            )
            
            # Create new filename with speed factor
            
            params = generation_params or {}
            # Include speed_factor in the filename for the final version
            filename_params = {**params, "speed_factor": speed_factor}
            
            speed_filename = generate_enhanced_filename("tts", filename_params, "wav")
            
            # Use same output directory logic as main generation (with project folder support)
            base_output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            project_folder = generation_params.get('project')
            if project_folder:
                output_dir = base_output_dir / project_folder
            else:
                output_dir = base_output_dir
                
            speed_output_path = output_dir / speed_filename
            
            # Save speed-adjusted audio
            torchaudio.save(str(speed_output_path), processed_audio, sample_rate)
            
            # Check and fix precision issues if needed (Task 11.11.1)
            # Some speed factor libraries may generate 64-bit files, normalize to 32-bit
            from utils.audio.analysis import normalize_audio_format_file
            speed_output_path = normalize_audio_format_file(Path(speed_output_path))
            
            logger.info(f"Speed factor {speed_factor}x applied successfully: {speed_output_path}")
            
            return str(speed_output_path)
            
        except Exception as e:
            logger.error(f"Speed factor post-processing failed: {e}")
            # Return original path as fallback
            return audio_path

    def _apply_trimming_post_processing(self, audio_path: str, generation_params: Dict[str, Any]) -> str:
        """
        Apply audio trimming as post-processing step (Task 11.4)
        
        This method trims silence from beginning and end of generated TTS audio,
        applied after speed factor processing and before secondary format generation.
        """
        try:
            logger.info("Applying audio trimming as post-processing")
            
            # Get trimming parameters
            trim_threshold_ms = generation_params.get('trim_threshold_ms', 200)
            
            # Load audio as AudioSegment for processing
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_wav(audio_path)
            
            # Apply trimming using existing utility function
            trim_result = apply_audio_trimming(
                audio_segment=audio_segment,
                filename=Path(audio_path).name,
                trim_threshold_ms=trim_threshold_ms
            )
            
            if trim_result["trimmed"]:
                # Create new filename with trim parameters
                
                params = generation_params or {}
                filename_params = {
                    'temperature': params.get('temperature', 0.75),
                    'seed': params.get('seed', 0),
                    'speed_factor': params.get('speed_factor', 1.0),
                    'trim': True,
                    'trim_threshold_ms': trim_threshold_ms
                }
                
                trim_filename = generate_enhanced_filename("tts", filename_params, "wav")
                
                # Use same output directory logic as main generation (with project folder support)
                base_output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
                project_folder = generation_params.get('project')
                if project_folder:
                    output_dir = base_output_dir / project_folder
                else:
                    output_dir = base_output_dir
                    
                trim_output_path = output_dir / trim_filename
                
                # Save trimmed audio
                trim_result["audio_segment"].export(str(trim_output_path), format="wav")
                
                logger.info(f"Audio trimming applied successfully: {trim_output_path}")
                logger.info(f"Trimmed duration: {trim_result['original_duration_ms']}ms → {trim_result['trimmed_duration_ms']}ms")
                logger.info(f"Removed silence: {trim_result['leading_silence_removed_ms']}ms (start) + {trim_result['trailing_silence_removed_ms']}ms (end)")
                
                return str(trim_output_path)
            else:
                logger.info("No significant silence detected, trimming skipped")
                return audio_path
                
        except Exception as e:
            logger.error(f"Audio trimming post-processing failed: {e}")
            # Return original path as fallback
            return audio_path
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        if not config_manager.get("api.cleanup_temp_files", True):
            return
            
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        self._temp_files.clear()

    def generate_vc(self, **kwargs) -> Dict:
        """
        Generate Voice Conversion - SYNCHRONOUS VERSION for performance
        Returns dictionary with output_files, processing_time, etc.
        """
        start_time = time.time()
        
        with logger.operation_timer("vc_generation", record_metrics=True):
            try:
                # Load model
                vc_model = get_or_load_vc_model()
                
                # Extract and validate parameters
                input_source = kwargs.get('input_audio_source', '').strip()
                target_source = kwargs.get('target_voice_source', '').strip()
                
                if not input_source or not target_source:
                    raise ValidationError("Both input and target audio sources are required")
                
                logger.info("Starting VC generation",
                           extra_data={'input_source': input_source, 'target_source': target_source})
                
                # Resolve audio paths (handles URLs and local files)
                input_path = self.resolve_audio_path(input_source, "vc_input")
                target_path = self.resolve_audio_path(target_source, "vc_target")
                
                logger.info(f"Using input audio: {input_path}")
                logger.info(f"Using target voice: {target_path}")
                
                # Update voice usage statistics for target voice
                try:
                    update_voice_usage(target_path)
                except Exception as e:
                    logger.warning(f"Failed to update voice usage: {e}")
                
                # Call the VC generation logic
                wav_output_path = self._process_vc_generation_sync(input_path, target_path, **kwargs)
                
                # Convert to requested formats
                export_formats = kwargs.get('export_formats', ['wav', 'mp3'])
                output_files = self.convert_audio_formats(wav_output_path, export_formats)
                
                processing_time = time.time() - start_time
                
                # Save generation metadata
                metadata = {
                    'type': 'vc',
                    'parameters': {
                        'input_audio_source': input_source,
                        'target_voice_source': target_source,
                        'chunk_sec': kwargs.get('chunk_sec', 60),
                        'overlap_sec': kwargs.get('overlap_sec', 0.1),
                        'disable_watermark': kwargs.get('disable_watermark', True),
                        'export_formats': export_formats
                    },
                    'generation_info': {
                        'processing_time_seconds': processing_time,
                        'input_path': str(input_path),
                        'target_path': str(target_path)
                    },
                    'files': {file['format']: file['filename'] for file in output_files}
                }
                
                # Save metadata using utility function
                if output_files:
                    save_generation_metadata(output_files[0]['filename'], metadata)
                
                return {
                    'success': True,
                    'output_files': output_files,
                    'processing_time_seconds': processing_time,
                    'message': 'Voice conversion completed successfully'
                }
                
            except Exception as e:
                logger.error(f"VC generation failed: {e}")
                if isinstance(e, (ValidationError, ResourceError, ModelLoadError)):
                    raise
                else:
                    raise GenerationError(f"VC generation failed: {e}")
    
    def _process_vc_generation_sync(self, input_path: Path, target_path: Path, **kwargs) -> Path:
        """
        VC generation
        """
        try:
            import soundfile as sf
            import librosa
            
            vc_model = get_or_load_vc_model()
            model_sr = vc_model.sr
            
            # Extract parameters
            chunk_sec = kwargs.get('chunk_sec', 60)
            overlap_sec = kwargs.get('overlap_sec', 0.1)
            disable_watermark = kwargs.get('disable_watermark', True)
            
            # Prepare output directory
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            output_dir.mkdir(exist_ok=True)
            temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
            temp_dir.mkdir(exist_ok=True)
            
            # Load and prepare input audio
            wav, sr = sf.read(str(input_path))
            if wav.ndim > 1:
                wav = wav.mean(axis=1)
            if sr != model_sr:
                wav = librosa.resample(wav, orig_sr=sr, target_sr=model_sr)
                sr = model_sr
            
            total_sec = len(wav) / model_sr
            logger.info(f"Input audio: {total_sec:.2f} seconds")
            
            # Generate enhanced output filename
            vc_params = {
                'chunk_sec': kwargs.get('chunk_sec', 60),
                'overlap_sec': kwargs.get('overlap_sec', 0.1),
                'target_voice_source': kwargs.get('target_voice_source', 'unknown')
            }
            filename = generate_enhanced_filename("vc", vc_params, "wav")
            output_path = output_dir / filename
            
            if total_sec <= chunk_sec:
                # Short audio - process directly
                logger.info("Processing short audio directly")
                wav_out = vc_model.generate(
                    str(input_path),
                    target_voice_path=str(target_path),
                    apply_watermark=not disable_watermark
                )
                out_wav = wav_out.squeeze(0).numpy()
                
                # Save the result
                sf.write(str(output_path), out_wav, model_sr)
                
            else:
                # Long audio - implement chunking with crossfading
                logger.info(f"Processing long audio with chunking: {chunk_sec}s chunks, {overlap_sec}s overlap")
                chunk_samples = int(chunk_sec * model_sr)
                overlap_samples = int(overlap_sec * model_sr)
                step_samples = chunk_samples - overlap_samples
                
                out_chunks = []
                
                for start in range(0, len(wav), step_samples):
                    end = min(start + chunk_samples, len(wav))
                    chunk = wav[start:end]
                    
                    # Create temporary chunk file
                    temp_chunk_path = temp_dir / f"temp_vc_chunk_{start}_{end}.wav"
                    sf.write(str(temp_chunk_path), chunk, model_sr)
                    self._temp_files.append(temp_chunk_path)  # Track for cleanup
                    
                    # Process chunk
                    try:
                        out_chunk = vc_model.generate(
                            str(temp_chunk_path),
                            target_voice_path=str(target_path),
                            apply_watermark=not disable_watermark
                        )
                        out_chunk_np = out_chunk.squeeze(0).numpy()
                        out_chunks.append(out_chunk_np)
                        logger.debug(f"Chunk {start}-{end} processed successfully")
                    except Exception as e:
                        logger.error(f"Failed to process chunk {start}-{end}: {e}")
                        # Use silence as fallback
                        silence_samples = len(chunk)
                        out_chunks.append(np.zeros(silence_samples, dtype=np.float32))
                
                if not out_chunks:
                    raise GenerationError("No chunks were processed successfully")
                
                # Combine chunks with crossfading
                logger.info("Combining chunks with crossfading...")
                result = out_chunks[0]
                
                for i in range(1, len(out_chunks)):
                    overlap = min(overlap_samples, len(out_chunks[i]), len(result))
                    if overlap > 0:
                        fade_out = np.linspace(1, 0, overlap)
                        fade_in = np.linspace(0, 1, overlap)
                        result[-overlap:] = result[-overlap:] * fade_out + out_chunks[i][:overlap] * fade_in
                        result = np.concatenate([result, out_chunks[i][overlap:]])
                    else:
                        result = np.concatenate([result, out_chunks[i]])
                
                # Save the combined result
                sf.write(str(output_path), result, model_sr)
                logger.info(f"Combined VC result saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"VC generation failed: {e}")
            raise GenerationError(f"VC generation failed: {e}")


# Global synchronous engine instance
engine = CoreEngine()
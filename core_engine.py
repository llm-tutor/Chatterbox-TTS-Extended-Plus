# Performance-optimized core_engine.py - synchronous version matching Chatter.py patterns
# This version removes async overhead that was causing 10x performance degradation

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
from utils import generate_unique_filename, validate_audio_file, sanitize_filename

# Whisper imports
import whisper
from faster_whisper import WhisperModel as FasterWhisperModel
import nltk
from nltk.tokenize import sent_tokenize

logger = get_logger(__name__)

# ===== GLOBAL VARIABLES (MATCHING CHATTER.PY PATTERNS) =====
# This matches the original Chatter.py approach for better performance
_tts_model: Optional[ChatterboxTTS] = None
_vc_model: Optional[ChatterboxVC] = None
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

def set_seed(seed: int) -> int:
    """Set random seed for reproducibility, returns actual seed used (matching Chatter.py)"""
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

# ===== HELPER FUNCTIONS (extracted from Chatter.py) =====

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

class CoreEngineSynchronous:
    """Synchronous core engine matching Chatter.py performance patterns"""
    
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
        """Convert WAV to additional formats"""
        output_files = []
        base_name = wav_path.stem
        output_dir = wav_path.parent
        
        for fmt in formats:
            fmt_lower = fmt.lower()
            if fmt_lower == 'wav':
                output_files.append({
                    'format': 'wav',
                    'filename': wav_path.name,
                    'url': f'/outputs/{wav_path.name}',
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
                        'url': f'/outputs/{output_path.name}',
                        'path': str(output_path)
                    })
                    
                    logger.debug(f"Converted to {fmt}: {output_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to convert to {fmt}: {e}")
                    logger.error(f"Conversion error details: {type(e).__name__}: {str(e)}")
                    # Continue with other formats
        
        return output_files
    
    def process_text_preprocessing(self, text: str, **kwargs) -> str:
        """Preprocess text with the same logic as Chatter.py"""
        
        # Apply preprocessing options
        if kwargs.get('to_lowercase', True):
            text = text.lower()
        
        if kwargs.get('normalize_spacing', True):
            text = normalize_whitespace(text)
        
        if kwargs.get('fix_dot_letters', True):
            text = replace_letter_period_sequences(text)
        
        if kwargs.get('remove_reference_numbers', True):
            text = remove_inline_reference_numbers(text)
        
        return text

    def process_one_chunk(self, model, sentence_group: str, idx: int, gen_index: int, this_seed: int,
                         audio_prompt_path_input: Optional[str], exaggeration_input: float, 
                         temperature_input: float, cfgw_input: float, disable_watermark: bool,
                         num_candidates_per_chunk: int, max_attempts_per_candidate: int,
                         bypass_whisper_checking: bool, retry_attempt_number: int = 1) -> Tuple[int, List[str]]:
        """
        Process one chunk of text - SYNCHRONOUS VERSION matching Chatter.py exactly
        This is the critical method that was causing the performance issue
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
                        
                        # This is the critical call - SYNCHRONOUS like original
                        wav = model.generate(
                            sentence_group,
                            audio_prompt_path=audio_prompt_path_input,
                            exaggeration=min(exaggeration_input, 1.0),
                            temperature=temperature_input,
                            cfg_weight=cfgw_input,
                            apply_watermark=not disable_watermark
                        )
                        
                        # Save candidate exactly like Chatter.py
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
                        candidates.append(str(candidate_path))
                        break  # Success, move to next candidate
                        
                    except Exception as e:
                        logger.error(f"Failed to generate candidate {cand_idx+1} attempt {attempt+1} for chunk {idx}: {e}")
                        continue
            
            return (idx, candidates)
            
        except Exception as e:
            logger.error(f"Error processing chunk {idx}: {e}")
            return (idx, [])

    def generate_tts(self, **kwargs) -> Dict:
        """
        Generate TTS audio - SYNCHRONOUS VERSION for performance
        Returns dictionary with output_files, seed_used, processing_time, etc.
        """
        start_time = time.time()
        
        with logger.operation_timer("tts_generation", record_metrics=True):
            try:
                # Load model synchronously like original Chatter.py
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
                        from utils import update_voice_usage
                        update_voice_usage(ref_audio_path)
                    except Exception as e:
                        logger.warning(f"Failed to update voice usage: {e}")
                
                # Process text with preprocessing options (exclude 'text' from kwargs to avoid duplicate)
                preprocessing_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
                processed_text = self.process_text_preprocessing(text, **preprocessing_kwargs)
                
                # Call the TTS generation logic (exclude 'text' from kwargs)
                generation_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
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
                from utils import save_generation_metadata
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
        SYNCHRONOUS TTS generation with chunking, retry, and Whisper validation
        This is the performance-critical method - matches Chatter.py patterns exactly
        """
        try:
            model = get_or_load_tts_model()
            
            # Prepare output directory and temp directory
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            output_dir.mkdir(exist_ok=True)
            temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
            temp_dir.mkdir(exist_ok=True)

            # Clean temp directory
            for f in temp_dir.iterdir():
                if f.is_file():
                    f.unlink()

            # Extract parameters with defaults (matching Chatter.py)
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
            
            # Process each sentence group - SYNCHRONOUS like original
            all_candidates = {}
            audio_prompt_path_str = str(ref_audio_path) if ref_audio_path else None
            
            for gen_index in range(num_generations):
                logger.info(f"Starting generation {gen_index + 1}/{num_generations}")
                generation_seed = random.randint(1, 2**32-1)
                
                for group_idx, sentence_group in enumerate(sentence_groups):
                    sentence_text = ' '.join(sentence_group)
                    
                    # Process this chunk synchronously - matching Chatter.py exactly
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
            
            # Select best candidates and combine (simplified for performance)
            logger.info("Selecting best candidates and combining...")
            
            # Simple strategy: take first candidate from each chunk
            final_chunks = []
            for gen_index in range(num_generations):
                gen_chunks = []
                for group_idx in range(len(sentence_groups)):
                    key = f"gen_{gen_index}_chunk_{group_idx}"
                    if key in all_candidates and all_candidates[key]:
                        gen_chunks.append(all_candidates[key][0])  # Take first candidate
                
                if gen_chunks:
                    # Phase 10.1.2 Optimization: Separate speed factor processing
                    # Step 1: Combine chunks (always at 1.0x speed)
                    combined_path = self._combine_audio_chunks(gen_chunks, gen_index, kwargs)
                    
                    # Step 2: Apply speed factor as post-processing if needed
                    speed_factor = kwargs.get('speed_factor', 1.0)
                    if abs(speed_factor - 1.0) >= 1e-6:
                        # Only apply speed factor processing if actually needed
                        combined_path = self.apply_speed_factor_post_processing(combined_path, speed_factor, kwargs)
                    
                    final_chunks.append(combined_path)
            
            if not final_chunks:
                raise GenerationError("No final audio chunks were created")
            
            # Return the first (and typically only) generation
            return Path(final_chunks[0])
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise GenerationError(f"TTS generation failed: {e}")

    def _combine_audio_chunks(self, chunk_paths: List[str], gen_index: int, generation_params: Dict[str, Any] = None) -> str:
        """
        Combine audio chunks into a single file
        
        Phase 10.1.2 Optimization: Speed factor processing moved to separate method
        This eliminates overhead for speed_factor=1.0 (most common case)
        """
        try:
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            
            # Use enhanced filename generation (excluding speed_factor for base file)
            from utils import generate_enhanced_filename
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
            from utils import apply_speed_factor
            processed_audio = apply_speed_factor(audio_tensor, sample_rate, speed_factor)
            
            # Create new filename with speed factor
            from utils import generate_enhanced_filename
            
            params = generation_params or {}
            # Include speed_factor in the filename for the final version
            filename_params = {**params, "speed_factor": speed_factor}
            
            speed_filename = generate_enhanced_filename("tts", filename_params, "wav")
            speed_output_path = Path(config_manager.get("paths.output_dir", "outputs")) / speed_filename
            
            # Save speed-adjusted audio
            torchaudio.save(str(speed_output_path), processed_audio, sample_rate)
            logger.info(f"Speed factor {speed_factor}x applied successfully: {speed_output_path}")
            
            return str(speed_output_path)
            
        except Exception as e:
            logger.error(f"Speed factor post-processing failed: {e}")
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
                # Load model synchronously like original Chatter.py
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
                    from utils import update_voice_usage
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
                from utils import save_generation_metadata
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
        SYNCHRONOUS VC generation matching Chatter.py patterns exactly
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
            
            # Load and prepare input audio (matching Chatter.py exactly)
            wav, sr = sf.read(str(input_path))
            if wav.ndim > 1:
                wav = wav.mean(axis=1)
            if sr != model_sr:
                wav = librosa.resample(wav, orig_sr=sr, target_sr=model_sr)
                sr = model_sr
            
            total_sec = len(wav) / model_sr
            logger.info(f"Input audio: {total_sec:.2f} seconds")
            
            # Generate enhanced output filename
            from utils import generate_enhanced_filename
            vc_params = {
                'chunk_sec': kwargs.get('chunk_sec', 60),
                'overlap_sec': kwargs.get('overlap_sec', 0.1),
                'target_voice_source': kwargs.get('target_voice_source', 'unknown')
            }
            filename = generate_enhanced_filename("vc", vc_params, "wav")
            output_path = output_dir / filename
            
            if total_sec <= chunk_sec:
                # Short audio - process directly (matching Chatter.py)
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
                # Long audio - implement chunking with crossfading (matching Chatter.py)
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
                
                # Combine chunks with crossfading (matching Chatter.py exactly)
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
engine_sync = CoreEngineSynchronous()
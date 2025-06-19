# core_engine.py - Phase 6: Complete TTS and VC Logic Extraction
# Full extraction from Chatter.py with chunking, retry, and Whisper validation

import os
import time
import random
import logging
import tempfile
import asyncio
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

logger = logging.getLogger(__name__)
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

def smart_append_short_sentences(sentences: List[str], min_chars: int = 50) -> List[List[str]]:
    """Smart batching: combine short sentences, keep long ones separate"""
    groups = []
    current_group = []
    current_chars = 0
    
    for sentence in sentences:
        sentence_chars = len(sentence)
        
        if sentence_chars >= min_chars * 2:  # Long sentence - process alone
            if current_group:
                groups.append(current_group)
                current_group = []
                current_chars = 0
            groups.append([sentence])
        else:  # Short sentence - try to combine
            if current_chars + sentence_chars > min_chars * 3 and current_group:
                groups.append(current_group)
                current_group = [sentence]
                current_chars = sentence_chars
            else:
                current_group.append(sentence)
                current_chars += sentence_chars
    
    if current_group:
        groups.append(current_group)
    
    return groups

def set_seed(seed_value: int) -> int:
    """Set random seed for reproducibility"""
    if seed_value <= 0:
        seed_value = random.randint(1, 2**32 - 1)
    
    torch.manual_seed(seed_value)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)
    random.seed(seed_value)
    np.random.seed(seed_value)
    
    logger.debug(f"Seed set to: {seed_value}")
    return seed_value

# ===== WHISPER HELPER FUNCTIONS =====

# Whisper model mapping
whisper_model_map = {
    "tiny": "tiny",
    "base": "base", 
    "small": "small",
    "medium": "medium",
    "large": "large-v2"
}

def load_whisper_backend(model_key: str, use_faster_whisper: bool, device: str):
    """Load Whisper model backend"""
    try:
        if use_faster_whisper:
            logger.info(f"Loading Faster-Whisper model: {model_key}")
            # For faster-whisper, device should be "cuda" or "cpu"
            device_type = "cuda" if device == "cuda" and torch.cuda.is_available() else "cpu"
            return FasterWhisperModel(model_key, device=device_type)
        else:
            logger.info(f"Loading OpenAI Whisper model: {model_key}")
            return whisper.load_model(model_key, device=device)
    except Exception as e:
        logger.error(f"Failed to load Whisper model {model_key}: {e}")
        # Fallback to base model
        try:
            if use_faster_whisper:
                device_type = "cuda" if device == "cuda" and torch.cuda.is_available() else "cpu"
                return FasterWhisperModel("base", device=device_type)
            else:
                return whisper.load_model("base", device=device)
        except Exception as e2:
            logger.error(f"Failed to load fallback Whisper model: {e2}")
            raise ModelLoadError(f"Could not load any Whisper model: {e}")

def whisper_check_mp(audio_path: str, expected_text: str, whisper_model, use_faster_whisper: bool) -> Tuple[str, float, str]:
    """Check audio quality using Whisper transcription"""
    try:
        if use_faster_whisper:
            # Faster-whisper API
            segments, info = whisper_model.transcribe(audio_path)
            transcribed = " ".join([segment.text for segment in segments]).strip()
        else:
            # OpenAI Whisper API
            result = whisper_model.transcribe(audio_path)
            transcribed = result["text"].strip()
        
        # Calculate similarity score
        expected_clean = expected_text.lower().strip()
        transcribed_clean = transcribed.lower().strip()
        
        if not expected_clean or not transcribed_clean:
            return audio_path, 0.0, transcribed
        
        # Use difflib for similarity calculation
        similarity = difflib.SequenceMatcher(None, expected_clean, transcribed_clean).ratio()
        
        logger.debug(f"Whisper check: expected='{expected_clean[:50]}...', got='{transcribed_clean[:50]}...', score={similarity:.3f}")
        
        return audio_path, similarity, transcribed
        
    except Exception as e:
        logger.error(f"Whisper transcription failed for {audio_path}: {e}")
        return audio_path, 0.0, ""

# ===== CORE ENGINE CLASS =====

class CoreEngine:
    """Core engine for TTS and VC operations with full feature extraction"""
    
    def __init__(self):
        # Model instances
        self.tts_model: Optional[ChatterboxTTS] = None
        self.vc_model: Optional[ChatterboxVC] = None
        self.whisper_model: Optional[Union[whisper.Whisper, FasterWhisperModel]] = None
        
        # Device and status tracking
        self.device = self._determine_device()
        self.models_loaded = {"tts": False, "vc": False, "whisper": False}
        
        # Temporary file tracking for cleanup
        self._temp_files = []
        
        logger.info(f"CoreEngine initialized with device: {self.device}")
        
    def _determine_device(self) -> str:
        """Determine the best device to use"""
        device_config = config_manager.get("models.device", "auto")
        
        if device_config == "auto":
            if torch.cuda.is_available():
                try:
                    # Test CUDA functionality
                    torch.zeros(1).cuda()
                    logger.info("CUDA available and functional")
                    return "cuda"
                except Exception as e:
                    logger.warning(f"CUDA available but not functional: {e}")
                    return "cpu"
            else:
                logger.info("CUDA not available")
                return "cpu"
        else:
            logger.info(f"Using configured device: {device_config}")
            return device_config
    
    # ===== MODEL LOADING METHODS =====
    
    async def load_tts_model(self) -> None:
        """Load TTS model"""
        if self.tts_model is not None:
            logger.info("TTS model already loaded")
            return
            
        try:
            logger.info(f"Loading TTS model on device: {self.device}")
            
            # Load the model (adapted from Chatter.py get_or_load_model)
            self.tts_model = ChatterboxTTS.from_pretrained(self.device)
            
            # Ensure model is on correct device
            if hasattr(self.tts_model, 'to') and str(getattr(self.tts_model, 'device', '')) != self.device:
                self.tts_model.to(self.device)
                
            self.models_loaded["tts"] = True
            logger.info(f"TTS model loaded successfully on device: {getattr(self.tts_model, 'device', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            self.models_loaded["tts"] = False
            raise ModelLoadError(f"TTS model loading failed: {e}")
    
    async def load_vc_model(self) -> None:
        """Load VC model"""
        if self.vc_model is not None:
            logger.info("VC model already loaded")
            return
            
        try:
            logger.info(f"Loading VC model on device: {self.device}")
            
            # Load the model (adapted from Chatter.py get_or_load_vc_model)
            self.vc_model = ChatterboxVC.from_pretrained(self.device)
            
            # Ensure model is on correct device
            if hasattr(self.vc_model, 'to') and str(getattr(self.vc_model, 'device', '')) != self.device:
                self.vc_model.to(self.device)
                
            self.models_loaded["vc"] = True
            logger.info(f"VC model loaded successfully on device: {getattr(self.vc_model, 'device', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to load VC model: {e}")
            self.models_loaded["vc"] = False
            raise ModelLoadError(f"VC model loading failed: {e}")
    
    async def load_whisper_model(self, model_name: str = "medium", use_faster_whisper: bool = True) -> None:
        """Load Whisper model for validation"""
        try:
            if self.whisper_model is not None:
                logger.info("Whisper model already loaded")
                return
            
            model_key = whisper_model_map.get(model_name, "medium")
            self.whisper_model = load_whisper_backend(model_key, use_faster_whisper, self.device)
            self.models_loaded["whisper"] = True
            logger.info(f"Whisper model loaded: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.models_loaded["whisper"] = False
            # Don't raise error - Whisper is optional
            
    async def ensure_models_loaded(self, tts: bool = False, vc: bool = False, whisper: bool = False, 
                                  whisper_model: str = "medium", use_faster_whisper: bool = True) -> None:
        """Ensure required models are loaded"""
        if tts and not self.models_loaded["tts"]:
            await self.load_tts_model()
        if vc and not self.models_loaded["vc"]:
            await self.load_vc_model()
        if whisper and not self.models_loaded["whisper"]:
            await self.load_whisper_model(whisper_model, use_faster_whisper)
    
    # ===== FILE HANDLING METHODS =====
    
    async def download_audio_file(self, url: str, destination: Path) -> Path:
        """Download audio file from URL"""
        try:
            timeout = config_manager.get("api.download_timeout_seconds", 30)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                destination.parent.mkdir(parents=True, exist_ok=True)
                with open(destination, 'wb') as f:
                    f.write(response.content)
                
                self._temp_files.append(destination)  # Track for cleanup
                logger.info(f"Downloaded {url} to {destination}")
                return destination
                
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise AudioProcessingError(f"Download failed: {e}")
    
    async def resolve_audio_path(self, source: str, context: str) -> Path:
        """
        Resolve audio file path based on context
        
        Args:
            source: filename, relative path, or URL
            context: 'tts_reference', 'vc_input', 'vc_target'
        """
        # Handle URLs - download to temp
        if source.startswith(('http://', 'https://')):
            # Validate URL safety
            from utils import validate_url
            if not validate_url(source):
                raise ResourceError(f"Invalid or unsafe URL: {source}")
                
            temp_dir = Path(config_manager.get("paths.temp_dir"))
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / f"download_{int(time.time())}_{hash(source) % 10000}.wav"
            return await self.download_audio_file(source, temp_file)
        
        # Determine base directory by context
        if context in ['tts_reference', 'vc_target']:
            base_dir = Path(config_manager.get("paths.reference_audio_dir"))
        elif context == 'vc_input':
            base_dir = Path(config_manager.get("paths.vc_input_dir"))
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
                logger.debug(f"Resolved audio path: {source} -> {path}")
                return path
        
        raise ResourceError(f"Audio file not found: {source} in {base_dir}")
    
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
                    
                    export_kwargs = {}
                    if fmt_lower == 'mp3':
                        export_kwargs['bitrate'] = '320k'
                    elif fmt_lower == 'flac':
                        export_kwargs['compression_level'] = 5
                    
                    audio.export(str(output_path), format=fmt_lower, **export_kwargs)
                    
                    output_files.append({
                        'format': fmt_lower,
                        'filename': output_path.name,
                        'url': f'/outputs/{output_path.name}',
                        'path': str(output_path)
                    })
                    
                    logger.debug(f"Converted to {fmt}: {output_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to convert to {fmt}: {e}")
                    # Continue with other formats
        
        return output_files
    
    # ===== TEXT PROCESSING METHODS =====
    
    def process_text_preprocessing(self, text: str, **kwargs) -> str:
        """Apply text preprocessing steps"""
        # Get preprocessing settings
        to_lowercase = kwargs.get('to_lowercase', True)
        normalize_spacing = kwargs.get('normalize_spacing', True)
        fix_dot_letters = kwargs.get('fix_dot_letters', True)
        remove_reference_numbers_flag = kwargs.get('remove_reference_numbers', True)
        
        original_text = text
        
        if to_lowercase:
            text = text.lower()
            
        if normalize_spacing:
            text = normalize_whitespace(text)
            
        if fix_dot_letters:
            text = replace_letter_period_sequences(text)
            
        if remove_reference_numbers_flag:
            text = remove_inline_reference_numbers(text)
        
        logger.debug(f"Text preprocessing: '{original_text[:50]}...' -> '{text[:50]}...'")
        return text.strip()
    
    # ===== CHUNK PROCESSING (extracted from Chatter.py) =====
    
    def process_one_chunk(self, model, sentence_group: List[str], chunk_idx: int, gen_index: int, 
                         seed_value: int, audio_prompt_path: Optional[str], exaggeration: float, 
                         temperature: float, cfg_weight: float, disable_watermark: bool, 
                         num_candidates: int, max_attempts: int, bypass_whisper: bool, 
                         attempt_num: int = 1) -> Tuple[int, List[Dict]]:
        """
        Process one chunk of text for TTS generation (extracted from Chatter.py)
        """
        set_seed(seed_value + chunk_idx + attempt_num)
        
        # Join sentences in the group
        text_chunk = " ".join(sentence_group)
        logger.debug(f"Processing chunk {chunk_idx}, attempt {attempt_num}: '{text_chunk[:50]}...'")
        
        candidates = []
        temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
        temp_dir.mkdir(exist_ok=True)
        
        for candidate_idx in range(num_candidates):
            try:
                # Generate unique filename for this candidate
                timestamp = int(time.time())
                temp_filename = f"chunk_{gen_index}_{chunk_idx}_{attempt_num}_{candidate_idx}_{timestamp}.wav"
                temp_path = temp_dir / temp_filename
                
                # Generate audio for this chunk
                wav = model.generate(
                    text_chunk,
                    audio_prompt_path=audio_prompt_path,
                    exaggeration=min(exaggeration, 1.0),
                    temperature=temperature,
                    cfg_weight=cfg_weight,
                    apply_watermark=not disable_watermark
                )
                
                # Save the candidate
                torchaudio.save(str(temp_path), wav, model.sr)
                self._temp_files.append(temp_path)  # Track for cleanup
                
                # Calculate duration
                duration = len(wav[0]) / model.sr if wav.ndim > 1 else len(wav) / model.sr
                
                candidates.append({
                    'path': str(temp_path),
                    'sentence_group': sentence_group,
                    'duration': duration,
                    'chunk_idx': chunk_idx,
                    'candidate_idx': candidate_idx
                })
                
                logger.debug(f"Generated candidate {candidate_idx} for chunk {chunk_idx}: {temp_filename}")
                
            except Exception as e:
                logger.error(f"Failed to generate candidate {candidate_idx} for chunk {chunk_idx}: {e}")
                continue
        
        return chunk_idx, candidates
    
    # ===== MAIN GENERATION METHODS =====
    
    async def generate_tts(self, **kwargs) -> Dict:
        """
        Generate TTS audio with full feature extraction from Chatter.py
        Returns dictionary with output_files, seed_used, processing_time, etc.
        """
        start_time = time.time()
        
        try:
            await self.ensure_models_loaded(tts=True)
            
            # Extract and validate parameters
            text = kwargs.get('text', '').strip()
            if not text:
                raise ValidationError("Text cannot be empty")
            
            # Validate text length
            max_length = config_manager.get("api.max_text_length", 10000)
            if len(text) > max_length:
                raise ValidationError(f"Text too long. Maximum length: {max_length} characters")
            
            # Handle seed
            seed = kwargs.get('seed', 0)
            actual_seed = set_seed(seed)
            
            # Handle reference audio
            ref_audio_path = None
            if kwargs.get('reference_audio_filename'):
                ref_audio_path = await self.resolve_audio_path(
                    kwargs['reference_audio_filename'], 
                    'tts_reference'
                )
                logger.info(f"Using reference audio: {ref_audio_path}")
            
            # Process text with preprocessing options (exclude 'text' from kwargs to avoid duplicate)
            preprocessing_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
            processed_text = self.process_text_preprocessing(text, **preprocessing_kwargs)
            
            # Call the full TTS generation logic (exclude 'text' from kwargs)
            generation_kwargs = {k: v for k, v in kwargs.items() if k != 'text'}
            wav_output_path = await self._process_tts_generation_full(processed_text, ref_audio_path, **generation_kwargs)
            
            # Convert to requested formats
            export_formats = kwargs.get('export_formats', ['wav', 'mp3'])
            output_files = self.convert_audio_formats(wav_output_path, export_formats)
            
            processing_time = time.time() - start_time
            
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
    
    async def generate_vc(self, **kwargs) -> Dict:
        """
        Generate voice conversion with full feature extraction from Chatter.py
        Returns dictionary with output_files, processing_time, etc.
        """
        start_time = time.time()
        
        try:
            await self.ensure_models_loaded(vc=True)
            
            input_source = kwargs.get('input_audio_source', '').strip()
            target_source = kwargs.get('target_voice_source', '').strip()
            
            if not input_source or not target_source:
                raise ValidationError("Both input and target audio sources are required")
            
            # Resolve audio paths (handles URLs and local files)
            input_path = await self.resolve_audio_path(input_source, "vc_input")
            target_path = await self.resolve_audio_path(target_source, "vc_target")
            
            logger.info(f"Voice conversion: {input_path} -> {target_path}")
            
            # Call the full VC generation logic
            wav_output_path = await self._process_vc_generation_full(input_path, target_path, **kwargs)
            
            # Convert to requested formats
            export_formats = kwargs.get('export_formats', ['wav', 'mp3'])
            output_files = self.convert_audio_formats(wav_output_path, export_formats)
            
            processing_time = time.time() - start_time
            
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

    # ===== FULL TTS GENERATION (extracted from Chatter.py) =====

    async def _process_tts_generation_full(self, text: str, ref_audio_path: Optional[Path],
                                           **kwargs) -> Path:
        """
        Full TTS generation with chunking, retry, and Whisper validation (extracted from Chatter.py)
        """
        try:
            if self.tts_model is None:
                raise ModelLoadError("TTS model not loaded")

            # Prepare output directory and temp directory
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            output_dir.mkdir(exist_ok=True)
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
            enable_parallel = kwargs.get('enable_parallel', False)
            num_parallel_workers = kwargs.get('num_parallel_workers', 4)

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
            
            # Process generations
            output_paths = []
            for gen_index in range(num_generations):
                if kwargs.get('seed', 0) == 0:
                    this_seed = random.randint(1, 2**32 - 1)
                else:
                    this_seed = int(kwargs.get('seed', 0)) + gen_index
                set_seed(this_seed)
                
                logger.info(f"Starting generation {gen_index+1}/{num_generations} with seed {this_seed}")
                
                chunk_candidate_map = {}
                
                # -------- CHUNK GENERATION --------
                if enable_parallel:
                    total_chunks = len(sentence_groups)
                    completed = 0
                    with ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
                        futures = [
                            executor.submit(
                                self.process_one_chunk,
                                self.tts_model, group, idx, gen_index, this_seed,
                                str(ref_audio_path) if ref_audio_path else None,
                                exaggeration, temperature, cfg_weight, disable_watermark,
                                num_candidates_per_chunk, max_attempts_per_candidate, bypass_whisper_checking
                            )
                            for idx, group in enumerate(sentence_groups)
                        ]
                        for future in as_completed(futures):
                            idx, candidates = future.result()
                            chunk_candidate_map[idx] = candidates
                            completed += 1
                            percent = int(100 * completed / total_chunks)
                            logger.info(f"Generated chunk {completed}/{total_chunks} ({percent}%)")
                else:
                    # Sequential mode: Process chunks one by one
                    for idx, group in enumerate(sentence_groups):
                        idx, candidates = self.process_one_chunk(
                            self.tts_model, group, idx, gen_index, this_seed,
                            str(ref_audio_path) if ref_audio_path else None,
                            exaggeration, temperature, cfg_weight, disable_watermark,
                            num_candidates_per_chunk, max_attempts_per_candidate, bypass_whisper_checking
                        )
                        chunk_candidate_map[idx] = candidates
                
                # -------- WHISPER VALIDATION --------
                if not bypass_whisper_checking:
                    await self.ensure_models_loaded(whisper=True, whisper_model=whisper_model_name, use_faster_whisper=use_faster_whisper)
                    
                    if self.whisper_model:
                        logger.info("Validating all candidates with Whisper...")
                        chunk_validations = {chunk_idx: [] for chunk_idx in chunk_candidate_map}
                        chunk_failed_candidates = {chunk_idx: [] for chunk_idx in chunk_candidate_map}
                        
                        # Initial sequential Whisper validation
                        for chunk_idx, candidates in chunk_candidate_map.items():
                            sentence_group = sentence_groups[chunk_idx]
                            expected_text = " ".join(sentence_group)
                            
                            for cand in candidates:
                                candidate_path = cand['path']
                                try:
                                    if not os.path.exists(candidate_path) or os.path.getsize(candidate_path) < 1024:
                                        logger.error(f"Candidate file missing or too small: {candidate_path}")
                                        chunk_failed_candidates[chunk_idx].append((0.0, candidate_path, ""))
                                        continue
                                    
                                    path, score, transcribed = whisper_check_mp(candidate_path, expected_text, self.whisper_model, use_faster_whisper)
                                    logger.debug(f"[Chunk {chunk_idx}] {os.path.basename(candidate_path)}: score={score:.3f}, transcript='{transcribed[:50]}...'")
                                    
                                    if score >= 0.95:
                                        chunk_validations[chunk_idx].append((cand['duration'], cand['path']))
                                    else:
                                        chunk_failed_candidates[chunk_idx].append((score, cand['path'], transcribed))
                                        
                                except Exception as e:
                                    logger.error(f"Whisper transcription failed for {candidate_path}: {e}")
                                    chunk_failed_candidates[chunk_idx].append((0.0, candidate_path, ""))
                        
                        # Retry logic for failed chunks
                        retry_queue = [chunk_idx for chunk_idx in sorted(chunk_candidate_map.keys()) if not chunk_validations[chunk_idx]]
                        chunk_attempts = {chunk_idx: 1 for chunk_idx in retry_queue}
                        
                        while retry_queue:
                            still_need_retry = [
                                chunk_idx for chunk_idx in retry_queue
                                if chunk_attempts[chunk_idx] < max_attempts_per_candidate
                            ]
                            if not still_need_retry:
                                break
                            
                            logger.info(f"Retrying {len(still_need_retry)} chunks, attempt {chunk_attempts[still_need_retry[0]]+1} of {max_attempts_per_candidate}")
                            
                            retry_candidate_map = {}
                            with ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
                                futures = [
                                    executor.submit(
                                        self.process_one_chunk,
                                        self.tts_model,
                                        sentence_groups[chunk_idx],
                                        chunk_idx,
                                        gen_index,
                                        random.randint(1, 2**32-1),
                                        str(ref_audio_path) if ref_audio_path else None,
                                        exaggeration, temperature, cfg_weight, disable_watermark,
                                        num_candidates_per_chunk, 1, bypass_whisper_checking,
                                        chunk_attempts[chunk_idx] + 1
                                    )
                                    for chunk_idx in still_need_retry
                                ]
                                for future in as_completed(futures):
                                    idx, candidates = future.result()
                                    retry_candidate_map[idx] = candidates
                            
                            # Validate retry candidates
                            for chunk_idx, candidates in retry_candidate_map.items():
                                sentence_group = sentence_groups[chunk_idx]
                                expected_text = " ".join(sentence_group)
                                
                                for cand in candidates:
                                    candidate_path = cand['path']
                                    try:
                                        if not os.path.exists(candidate_path) or os.path.getsize(candidate_path) < 1024:
                                            logger.error(f"Retry candidate file missing or too small: {candidate_path}")
                                            continue
                                        
                                        path, score, transcribed = whisper_check_mp(candidate_path, expected_text, self.whisper_model, use_faster_whisper)
                                        logger.debug(f"[Retry Chunk {chunk_idx}] {os.path.basename(candidate_path)}: score={score:.3f}")
                                        
                                        if score >= 0.95:
                                            chunk_validations[chunk_idx].append((cand['duration'], cand['path']))
                                            break  # Found a good candidate, stop retrying this chunk
                                        else:
                                            chunk_failed_candidates[chunk_idx].append((score, candidate_path, transcribed))
                                            
                                    except Exception as e:
                                        logger.error(f"Whisper retry validation failed for {candidate_path}: {e}")
                                        continue
                                
                                chunk_attempts[chunk_idx] += 1
                            
                            # Update retry queue - remove chunks that now have valid candidates
                            retry_queue = [chunk_idx for chunk_idx in retry_queue if not chunk_validations[chunk_idx]]
                        
                        # Handle final fallback for chunks that still failed
                        if use_longest_transcript_on_fail:
                            for chunk_idx in retry_queue:
                                if chunk_failed_candidates[chunk_idx]:
                                    # Sort by score and pick the best one
                                    best_failed = max(chunk_failed_candidates[chunk_idx], key=lambda x: x[0])
                                    logger.warning(f"Using best failed candidate for chunk {chunk_idx}: score={best_failed[0]:.3f}")
                                    chunk_validations[chunk_idx].append((0.0, best_failed[1]))  # Duration 0 for failed
                        
                        # Select final candidates (shortest duration for each chunk)
                        final_candidates = []
                        for chunk_idx in sorted(chunk_validations.keys()):
                            if chunk_validations[chunk_idx]:
                                # Sort by duration and pick shortest
                                best_candidate = min(chunk_validations[chunk_idx], key=lambda x: x[0])
                                final_candidates.append(best_candidate[1])
                            else:
                                logger.error(f"No valid candidate found for chunk {chunk_idx}")
                                raise GenerationError(f"Failed to generate valid audio for chunk {chunk_idx}")
                    else:
                        logger.warning("Whisper model not loaded, skipping validation")
                        # Use first candidate from each chunk
                        final_candidates = []
                        for chunk_idx in sorted(chunk_candidate_map.keys()):
                            if chunk_candidate_map[chunk_idx]:
                                final_candidates.append(chunk_candidate_map[chunk_idx][0]['path'])
                else:
                    # No Whisper validation - use first candidate from each chunk
                    final_candidates = []
                    for chunk_idx in sorted(chunk_candidate_map.keys()):
                        if chunk_candidate_map[chunk_idx]:
                            final_candidates.append(chunk_candidate_map[chunk_idx][0]['path'])
                
                # -------- COMBINE CHUNKS --------
                if len(final_candidates) == 0:
                    raise GenerationError("No valid audio chunks generated")
                elif len(final_candidates) == 1:
                    # Single chunk - just copy it
                    single_chunk_path = final_candidates[0]
                    output_filename = f"tts_output_{int(time.time())}_{this_seed}.wav"
                    output_path = output_dir / output_filename
                    
                    # Copy the file
                    import shutil
                    shutil.copy2(single_chunk_path, output_path)
                else:
                    # Multiple chunks - concatenate them
                    combined_audio = []
                    
                    for chunk_path in final_candidates:
                        try:
                            wav_chunk, sr = torchaudio.load(chunk_path)
                            combined_audio.append(wav_chunk)
                        except Exception as e:
                            logger.error(f"Failed to load chunk {chunk_path}: {e}")
                            continue
                    
                    if not combined_audio:
                        raise GenerationError("Failed to load any audio chunks")
                    
                    # Concatenate all chunks
                    final_audio = torch.cat(combined_audio, dim=1)
                    
                    # Save combined result
                    output_filename = f"tts_output_{int(time.time())}_{this_seed}.wav"
                    output_path = output_dir / output_filename
                    torchaudio.save(str(output_path), final_audio, self.tts_model.sr)
                
                # Verify the file was created successfully
                if not output_path.exists() or output_path.stat().st_size < 1024:
                    raise GenerationError("Generated audio file is missing or too small")
                
                logger.info(f"TTS generation successful: {output_path}")
                output_paths.append(output_path)
            
            # Return the first (or only) generated file
            return output_paths[0]
            
        except Exception as e:
            logger.error(f"Full TTS generation failed: {e}")
            if isinstance(e, (ModelLoadError, GenerationError)):
                raise
            else:
                raise GenerationError(f"TTS generation failed: {e}")
    
    # ===== FULL VC GENERATION (extracted from Chatter.py) =====
    
    async def _process_vc_generation_full(self, input_path: Path, target_path: Path, **kwargs) -> Path:
        """
        Full voice conversion with advanced chunking (extracted from Chatter.py)
        """
        try:
            if self.vc_model is None:
                raise ModelLoadError("VC model not loaded")
            
            # Prepare output directory
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            output_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            output_filename = f"vc_output_{timestamp}.wav"
            output_path = output_dir / output_filename
            
            # Extract VC parameters with defaults
            chunk_sec = kwargs.get('chunk_sec', config_manager.get("vc_defaults.chunk_sec", 60))
            overlap_sec = kwargs.get('overlap_sec', config_manager.get("vc_defaults.overlap_sec", 0.1))
            disable_watermark = kwargs.get('disable_watermark', config_manager.get("vc_defaults.disable_watermark", True))
            
            logger.info(f"Generating VC with params: chunk_sec={chunk_sec}, overlap_sec={overlap_sec}")
            
            # Read and prepare input audio
            wav, sr = sf.read(str(input_path))
            if wav.ndim > 1:
                wav = wav.mean(axis=1)  # Convert to mono
            
            model_sr = self.vc_model.sr
            if sr != model_sr:
                wav = librosa.resample(wav, orig_sr=sr, target_sr=model_sr)
                sr = model_sr
            
            total_sec = len(wav) / model_sr
            logger.info(f"Input audio duration: {total_sec:.2f} seconds")
            
            if total_sec <= chunk_sec:
                # Short audio - process directly without chunking
                logger.info("Processing short audio without chunking")
                wav_out = self.vc_model.generate(
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
                temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
                temp_dir.mkdir(exist_ok=True)
                
                num_chunks = (len(wav) + step_samples - 1) // step_samples
                logger.info(f"Will process {num_chunks} chunks")
                
                for chunk_idx, start in enumerate(range(0, len(wav), step_samples)):
                    end = min(start + chunk_samples, len(wav))
                    chunk = wav[start:end]
                    
                    logger.info(f"Processing chunk {chunk_idx + 1}/{num_chunks}: samples {start}-{end}")
                    
                    # Create temporary chunk file
                    temp_chunk_path = temp_dir / f"temp_vc_chunk_{chunk_idx}_{start}_{end}.wav"
                    sf.write(str(temp_chunk_path), chunk, model_sr)
                    self._temp_files.append(temp_chunk_path)  # Track for cleanup
                    
                    # Process chunk
                    try:
                        out_chunk = self.vc_model.generate(
                            str(temp_chunk_path),
                            target_voice_path=str(target_path),
                            apply_watermark=not disable_watermark
                        )
                        out_chunk_np = out_chunk.squeeze(0).numpy()
                        out_chunks.append(out_chunk_np)
                        logger.debug(f"Chunk {chunk_idx + 1} processed successfully")
                    except Exception as e:
                        logger.error(f"Failed to process chunk {chunk_idx + 1}: {e}")
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
                        # Create fade curves
                        fade_out = np.linspace(1, 0, overlap)
                        fade_in = np.linspace(0, 1, overlap)
                        
                        # Apply crossfade
                        result[-overlap:] = result[-overlap:] * fade_out + out_chunks[i][:overlap] * fade_in
                        
                        # Append remaining part of the chunk
                        if len(out_chunks[i]) > overlap:
                            result = np.concatenate([result, out_chunks[i][overlap:]])
                    else:
                        # No overlap - just concatenate
                        result = np.concatenate([result, out_chunks[i]])
                
                # Save the combined result
                sf.write(str(output_path), result, model_sr)
                logger.info(f"Combined {len(out_chunks)} chunks into final result")
            
            # Verify the file was created successfully
            if not output_path.exists() or output_path.stat().st_size < 1024:
                raise GenerationError("Generated VC audio file is missing or too small")
            
            logger.info(f"VC generation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Full VC generation failed: {e}")
            if isinstance(e, (ModelLoadError, GenerationError)):
                raise
            else:
                raise GenerationError(f"VC generation failed: {e}")
    
    # ===== CLEANUP METHODS =====
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        if not config_manager.get("api.cleanup_temp_files", True):
            logger.debug("Temp file cleanup disabled in config")
            return
            
        cleaned_count = 0
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")
        
        self._temp_files.clear()


# Global engine instance
engine = CoreEngine()

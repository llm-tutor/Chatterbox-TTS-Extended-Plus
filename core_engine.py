# core_engine.py - Refactored core TTS and VC logic
# Extracted from Chatter.py for shared use between Gradio UI and FastAPI

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

class CoreEngine:
    """Core engine for TTS and VC operations"""
    
    def __init__(self):
        # Model instances
        self.tts_model: Optional[ChatterboxTTS] = None
        self.vc_model: Optional[ChatterboxVC] = None
        
        # Device and status tracking
        self.device = self._determine_device()
        self.models_loaded = {"tts": False, "vc": False}
        
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
    
    async def ensure_models_loaded(self, tts: bool = False, vc: bool = False) -> None:
        """Ensure required models are loaded"""
        if tts and not self.models_loaded["tts"]:
            await self.load_tts_model()
        if vc and not self.models_loaded["vc"]:
            await self.load_vc_model()
    
    # ===== UTILITY METHODS =====
    
    def set_seed(self, seed_value: int) -> int:
        """Set random seed for reproducibility, returns actual seed used"""
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
    # (Extracted from Chatter.py)
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        return re.sub(r'\s{2,}', ' ', text.strip())

    def replace_letter_period_sequences(self, text: str) -> str:
        """Replace letter.period.sequences with spaced letters"""
        def replacer(match):
            cleaned = match.group(0).rstrip('.')
            letters = cleaned.split('.')
            return ' '.join(letters)
        
        pattern = r'\b[A-Za-z](?:\.[A-Za-z])*\.?'
        return re.sub(pattern, replacer, text)

    def remove_reference_numbers(self, text: str) -> str:
        """Remove reference numbers from text"""
        # Remove patterns like [1], [2], (1), (2), etc.
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\(\d+\)', '', text)
        return text

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
            text = self.normalize_whitespace(text)
            
        if fix_dot_letters:
            text = self.replace_letter_period_sequences(text)
            
        if remove_reference_numbers_flag:
            text = self.remove_reference_numbers(text)
        
        logger.debug(f"Text preprocessing: '{original_text[:50]}...' -> '{text[:50]}...'")
        return text.strip()
    
    # ===== MAIN GENERATION METHODS =====
    
    async def generate_tts(self, **kwargs) -> Dict:
        """
        Generate TTS audio
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
            actual_seed = self.set_seed(seed)
            
            # Handle reference audio
            ref_audio_path = None
            if kwargs.get('reference_audio_filename'):
                ref_audio_path = await self.resolve_audio_path(
                    kwargs['reference_audio_filename'], 
                    'tts_reference'
                )
                logger.info(f"Using reference audio: {ref_audio_path}")
            
            # Process text with preprocessing options
            processed_text = self.process_text_preprocessing(text, **kwargs)
            
            # Call the main TTS generation logic
            wav_output_path = await self._process_tts_generation(processed_text, ref_audio_path, **kwargs)
            
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
        Generate voice conversion
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
            
            # Call the main VC generation logic
            wav_output_path = await self._process_vc_generation(input_path, target_path, **kwargs)
            
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
            
            logger.info(f"VC generation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"VC generation failed: {e}")
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

    # ===== INTERNAL GENERATION METHODS =====
    # TODO: These are simplified implementations. 
    # Full extraction with chunking, retry, and Whisper validation to be implemented in Phase 6
    
    async def _process_tts_generation(self, text: str, ref_audio_path: Optional[Path], **kwargs) -> Path:
        """
        Process TTS generation (simplified version of Chatter.py logic)
        
        TODO PHASE 6: Implement full chunking, retry, and Whisper validation logic from Chatter.py
        Current implementation is basic single-call generation for API testing.
        """
        try:
            if self.tts_model is None:
                raise ModelLoadError("TTS model not loaded")
            
            # Prepare output directory
            output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
            output_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            seed_used = kwargs.get('seed', 0)
            output_filename = f"tts_output_{timestamp}_{seed_used}.wav"
            output_path = output_dir / output_filename
            
            # Extract TTS parameters with defaults
            exaggeration = kwargs.get('exaggeration', config_manager.get("tts_defaults.exaggeration", 0.5))
            temperature = kwargs.get('temperature', config_manager.get("tts_defaults.temperature", 0.75))
            cfg_weight = kwargs.get('cfg_weight', config_manager.get("tts_defaults.cfg_weight", 1.0))
            disable_watermark = kwargs.get('disable_watermark', config_manager.get("tts_defaults.disable_watermark", True))
            
            logger.info(f"Generating TTS with params: exaggeration={exaggeration}, temperature={temperature}, cfg_weight={cfg_weight}")
            
            # Call the TTS model (basic implementation)
            # Note: ref_audio_path could be None for prompt-free generation
            wav = self.tts_model.generate(
                text,
                audio_prompt_path=str(ref_audio_path) if ref_audio_path else None,
                exaggeration=min(exaggeration, 1.0),
                temperature=temperature,
                cfg_weight=cfg_weight,
                apply_watermark=not disable_watermark
            )
            
            # Save the generated audio
            torchaudio.save(str(output_path), wav, self.tts_model.sr)
            
            # Verify the file was created successfully
            if not output_path.exists() or output_path.stat().st_size < 1024:
                raise GenerationError("Generated audio file is missing or too small")
            
            logger.info(f"TTS generation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            if isinstance(e, (ModelLoadError, GenerationError)):
                raise
            else:
                raise GenerationError(f"TTS generation failed: {e}")
    
    async def _process_vc_generation(self, input_path: Path, target_path: Path, **kwargs) -> Path:
        """
        Process voice conversion (simplified version of Chatter.py logic)
        
        TODO PHASE 6: Enhance with advanced chunking strategies and edge case handling
        Current implementation has basic chunking with crossfading.
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
            
            if total_sec <= chunk_sec:
                # Short audio - process directly without chunking
                wav_out = self.vc_model.generate(
                    str(input_path),
                    target_voice_path=str(target_path),
                    apply_watermark=not disable_watermark
                )
                out_wav = wav_out.squeeze(0).numpy()
                
                # Save the result
                sf.write(str(output_path), out_wav, model_sr)
                
            else:
                # Long audio - implement chunking
                chunk_samples = int(chunk_sec * model_sr)
                overlap_samples = int(overlap_sec * model_sr)
                step_samples = chunk_samples - overlap_samples
                
                out_chunks = []
                temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
                temp_dir.mkdir(exist_ok=True)
                
                for start in range(0, len(wav), step_samples):
                    end = min(start + chunk_samples, len(wav))
                    chunk = wav[start:end]
                    
                    # Create temporary chunk file
                    temp_chunk_path = temp_dir / f"temp_vc_chunk_{start}_{end}.wav"
                    sf.write(str(temp_chunk_path), chunk, model_sr)
                    self._temp_files.append(temp_chunk_path)  # Track for cleanup
                    
                    # Process chunk
                    out_chunk = self.vc_model.generate(
                        str(temp_chunk_path),
                        target_voice_path=str(target_path),
                        apply_watermark=not disable_watermark
                    )
                    out_chunk_np = out_chunk.squeeze(0).numpy()
                    out_chunks.append(out_chunk_np)
                
                # Combine chunks with crossfading
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
            
            # Verify the file was created successfully
            if not output_path.exists() or output_path.stat().st_size < 1024:
                raise GenerationError("Generated VC audio file is missing or too small")
            
            logger.info(f"VC generation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"VC generation failed: {e}")
            if isinstance(e, (ModelLoadError, GenerationError)):
                raise
            else:
                raise GenerationError(f"VC generation failed: {e}")


# Global engine instance
engine = CoreEngine()

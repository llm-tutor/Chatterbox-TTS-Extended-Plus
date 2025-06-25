# utils.py - Utility functions for Chatterbox TTS Extended Plus

import os
import logging
import hashlib
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import torch
import random
import numpy as np

logger = logging.getLogger(__name__)


def parse_concat_files(files: List[str]) -> List[Dict[str, Union[str, int]]]:
    """
    Parse mixed file/silence array into processing instructions
    
    Args:
        files: List of filenames and silence notations like "(500ms)" or "(1.5s)"
    
    Returns:
        List of {"type": "file"|"silence", "source": str, "duration_ms": int}
        
    Raises:
        ValueError: If silence notation is invalid or duration out of range
    """
    silence_pattern = re.compile(r'^\((\d+(?:\.\d+)?)(ms|s)\)$')
    parsed_items = []
    
    for item in files:
        silence_match = silence_pattern.match(item)
        if silence_match:
            duration_value = float(silence_match.group(1))
            unit = silence_match.group(2)
            
            # Convert to milliseconds
            duration_ms = int(duration_value * 1000) if unit == 's' else int(duration_value)
            
            # Validate duration range (50ms to 10s)
            if not (50 <= duration_ms <= 10000):
                raise ValueError(f"Silence duration must be between 50ms and 10s, got: {item}")
            
            parsed_items.append({
                "type": "silence",
                "source": item,
                "duration_ms": duration_ms
            })
        else:
            parsed_items.append({
                "type": "file",
                "source": item,
                "duration_ms": 0  # Will be calculated from actual file
            })
    
    return parsed_items


def generate_silence_segment(duration_ms: int, sample_rate: int = 22050) -> 'AudioSegment':
    """
    Generate a silence segment of specified duration
    
    Args:
        duration_ms: Duration in milliseconds
        sample_rate: Target sample rate (match other audio)
    
    Returns:
        AudioSegment containing silence
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required for silence generation")
    
    return AudioSegment.silent(duration=duration_ms, frame_rate=sample_rate)


def generate_unique_filename(prefix: str = "output", extension: str = "wav") -> str:
    """Generate a unique filename with timestamp and hash"""
    timestamp = int(time.time())
    random_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_hash}.{extension}"


def generate_enhanced_filename(generation_type: str, parameters: Dict[str, Any], extension: str = "wav") -> str:
    """
    Generate enhanced filename with timestamp and key parameters
    
    Format: {type}_{timestamp}_{microseconds}_{key_params}.{ext}
    
    Args:
        generation_type: 'tts', 'vc', or 'concat'
        parameters: Dictionary of generation parameters
        extension: File extension (wav, mp3, etc.)
    
    Returns:
        Enhanced filename string
    """
    from datetime import datetime
    
    # Get current timestamp with microseconds
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    microseconds = now.microsecond
    
    # Extract key parameters based on generation type
    param_parts = []
    
    if generation_type == "tts":
        # Include key TTS parameters
        if "temperature" in parameters:
            param_parts.append(f"temp{parameters['temperature']}")
        if "seed" in parameters and parameters["seed"] != 0:
            param_parts.append(f"seed{parameters['seed']}")
        if "exaggeration" in parameters and parameters["exaggeration"] != 0.5:
            param_parts.append(f"exag{parameters['exaggeration']}")
        if "speed_factor" in parameters and parameters["speed_factor"] != 1.0:
            param_parts.append(f"speed{parameters['speed_factor']}")
            
    elif generation_type == "vc":
        # Include key VC parameters
        if "chunk_sec" in parameters and parameters["chunk_sec"] != 60:
            param_parts.append(f"chunk{parameters['chunk_sec']}")
        if "overlap_sec" in parameters and parameters["overlap_sec"] != 0.1:
            param_parts.append(f"overlap{parameters['overlap_sec']}")
        # Include reference to target voice if available
        if "target_voice_source" in parameters:
            voice_name = Path(parameters["target_voice_source"]).stem
            # Sanitize and truncate voice name
            voice_name = re.sub(r'[^\w\-]', '', voice_name)[:10]
            param_parts.append(f"voice{voice_name}")
            
    elif generation_type == "concat":
        # Include concat-specific parameters
        if "file_count" in parameters:
            param_parts.append(f"{parameters['file_count']}files")
        
        # Add silence count if manual silences were used
        if "silence_segments" in parameters and parameters["silence_segments"] > 0:
            param_parts.append(f"sil{parameters['silence_segments']}")
        
        # Add pause parameters only if not using manual silence
        if not parameters.get("manual_silence", False):
            if "pause_duration_ms" in parameters and parameters["pause_duration_ms"] > 0:
                pause_ms = parameters["pause_duration_ms"]
                variation_ms = parameters.get("pause_variation_ms", 0)
                if variation_ms > 0:
                    param_parts.append(f"pause{pause_ms}v{variation_ms}")
                else:
                    param_parts.append(f"pause{pause_ms}")
        
        if "crossfade_ms" in parameters and parameters["crossfade_ms"] > 0:
            param_parts.append(f"fade{parameters['crossfade_ms']}")
        if "normalize_levels" in parameters and parameters["normalize_levels"]:
            param_parts.append("leveled")
    
    # Construct filename
    param_string = "_".join(param_parts) if param_parts else "default"
    
    return f"{generation_type}_{timestamp}_{microseconds:06d}_{param_string}.{extension}"


def save_generation_metadata(filename: str, generation_data: Dict[str, Any]) -> bool:
    """
    Save generation metadata as JSON companion file
    
    Args:
        filename: Base filename (without path)
        generation_data: Complete generation context and parameters
    
    Returns:
        True if metadata saved successfully, False otherwise
    """
    import json
    from datetime import datetime
    from config import config_manager
    
    try:
        # Get output directory
        output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        
        # Create metadata filename
        base_name = Path(filename).stem
        metadata_file = output_dir / f"{base_name}.json"
        
        # Add timestamp if not present
        if "timestamp" not in generation_data:
            generation_data["timestamp"] = datetime.now().isoformat()
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(generation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved: {metadata_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save metadata for {filename}: {e}")
        return False


def validate_audio_file(file_path: Path) -> bool:
    """Validate if file is a supported audio format"""
    if not file_path.exists():
        return False
    
    supported_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    return file_path.suffix.lower() in supported_extensions


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    # Remove/replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    return filename


def get_audio_duration(file_path: Path) -> Optional[float]:
    """Get audio file duration in seconds"""
    try:
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            return len(f) / f.samplerate
    except Exception as e:
        logger.warning(f"Could not get duration for {file_path}: {e}")
        return None


def get_file_size(file_path: Path) -> Optional[int]:
    """Get file size in bytes"""
    try:
        return file_path.stat().st_size
    except Exception:
        return None


def ensure_directory_exists(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)


def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> None:
    """Clean up old files in directory"""
    if not directory.exists():
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    logger.debug(f"Cleaned up old file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {e}")


def is_url(text: str) -> bool:
    """Check if text is a valid URL"""
    return text.startswith(('http://', 'https://'))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def apply_speed_factor(
    audio_tensor: torch.Tensor, 
    sample_rate: int, 
    speed_factor: float,
    preferred_library: str = "auto"
) -> torch.Tensor:
    """
    Enhanced speed factor implementation for Phase 10.1.4 (Cleanup)
    
    Streamlined implementation focused on speech quality using audiostretchy
    as the primary enhanced library with clean fallback chain.
    
    Optimizations:
    - Early return for speed_factor=1.0 (zero overhead)
    - audiostretchy preferred for superior speech quality (TDHS algorithm)
    - Clean fallback chain: audiostretchy → librosa → torchaudio
    - Removed pyrubberband (artifacts make output unusable for speech)
    
    Args:
        audio_tensor: Input audio tensor (1D or 2D)
        sample_rate: Audio sample rate
        speed_factor: Speed multiplier (0.5x to 2.0x)
        preferred_library: Library preference - "auto", "audiostretchy", "librosa", "torchaudio"
    
    Returns:
        Speed-adjusted audio tensor with preserved pitch
    """
    # CRITICAL: Return immediately for 1.0 before any processing
    if speed_factor == 1.0:
        return audio_tensor
    
    # Get configuration limits
    from config import config_manager
    min_speed = config_manager.get("speed_factor.min_speed_factor", 0.5)
    max_speed = config_manager.get("speed_factor.max_speed_factor", 2.0)
    
    # Clamp speed factor to configured range
    speed_factor = max(min_speed, min(max_speed, speed_factor))
    
    # Smart library selection based on configuration and speed factor range
    if preferred_library == "auto":
        # Use configuration preference
        config_preferred = config_manager.get("speed_factor.preferred_library", "audiostretchy")
        
        # For speech processing, audiostretchy is preferred across all ranges
        if config_preferred == "audiostretchy":
            library_order = ["audiostretchy", "librosa", "torchaudio"]
        else:
            # Fallback to librosa-first if audiostretchy not configured
            library_order = ["librosa", "audiostretchy", "torchaudio"]
    else:
        # User specified a preferred library
        library_order = [preferred_library, "audiostretchy", "librosa", "torchaudio"]
    
    # Try each library in order
    for library in library_order:
        try:
            if library == "audiostretchy":
                return _apply_speed_audiostretchy(audio_tensor, sample_rate, speed_factor)
            elif library == "librosa":
                return _apply_speed_librosa(audio_tensor, sample_rate, speed_factor)
            elif library == "torchaudio":
                return _apply_speed_torchaudio(audio_tensor, sample_rate, speed_factor)
        except ImportError:
            logger.debug(f"Library {library} not available")
            continue
        except Exception as e:
            logger.warning(f"Speed factor with {library} failed: {e}")
            continue
    
    # If all libraries fail, return original audio
    logger.error("All speed factor libraries failed, returning original audio")
    return audio_tensor


def _apply_speed_audiostretchy(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """
    Apply speed factor using audiostretchy (TDHS algorithm)
    
    Best quality for speech, especially for small speed changes (±10%)
    Uses Time-Domain Harmonic Scaling with excellent formant preservation
    """
    try:
        from audiostretchy.stretch import stretch_audio
        import tempfile
        import soundfile as sf
        import os
        
        # Convert tensor to numpy
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.detach().cpu().numpy()
            original_device = audio_tensor.device
        else:
            audio_np = audio_tensor
            original_device = None
        
        # audiostretchy uses ratio (inverse of speed_factor)
        ratio = 1.0 / speed_factor
        
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
            temp_input_path = temp_input.name
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Write input audio to temp file
            if audio_np.ndim == 2:
                sf.write(temp_input_path, audio_np.T, sample_rate)  # Transpose for soundfile
            else:
                sf.write(temp_input_path, audio_np, sample_rate)
            
            # Process with audiostretchy (TDHS)
            stretch_audio(temp_input_path, temp_output_path, ratio=ratio)
            
            # Read processed result
            processed_audio, _ = sf.read(temp_output_path)
            
            # Handle channel dimensions correctly
            if audio_np.ndim == 2 and processed_audio.ndim == 2:
                processed_audio = processed_audio.T  # Transpose back
            elif audio_np.ndim == 2 and processed_audio.ndim == 1:
                processed_audio = processed_audio[np.newaxis, :]  # Add channel dimension
            elif audio_np.ndim == 1 and processed_audio.ndim == 2:
                processed_audio = processed_audio[:, 0]  # Take first channel
            
        finally:
            # Always cleanup temp files
            for temp_path in [temp_input_path, temp_output_path]:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass  # Ignore cleanup errors
        
        # Convert back to tensor
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except ImportError:
        raise ImportError("audiostretchy not available")
    except Exception as e:
        raise RuntimeError(f"audiostretchy processing failed: {e}")


def _apply_speed_librosa(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """
    Apply speed factor using librosa (basic phase vocoder)
    
    Good compatibility baseline with adequate quality for most uses
    Known to have some "phasiness" artifacts at extreme speed changes
    """
    try:
        import librosa.effects
        
        # Convert tensor to numpy array (minimize conversions)
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.detach().cpu().numpy()
            original_device = audio_tensor.device
        else:
            audio_np = audio_tensor
            original_device = None
        
        # Handle different tensor shapes efficiently
        if audio_np.ndim == 2:
            # Multi-channel audio - process each channel
            processed_channels = []
            for channel in range(audio_np.shape[0]):
                processed_channel = librosa.effects.time_stretch(
                    audio_np[channel], 
                    rate=speed_factor
                )
                processed_channels.append(processed_channel)
            processed_audio = np.stack(processed_channels, axis=0)
        else:
            # Single channel audio - direct processing
            processed_audio = librosa.effects.time_stretch(
                audio_np, 
                rate=speed_factor
            )
        
        # Convert back to tensor efficiently
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except ImportError:
        raise ImportError("librosa not available")
    except Exception as e:
        raise RuntimeError(f"librosa processing failed: {e}")


def _apply_speed_torchaudio(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """
    Fallback speed factor implementation using torchaudio resampling
    
    Note: This method does NOT preserve pitch and is less ideal than other methods
    Only used as a last resort when other libraries are unavailable
    """
    try:
        import torchaudio
        
        # Calculate new sample rate for speed adjustment
        new_sample_rate = int(sample_rate * speed_factor)
        
        # Resample to achieve speed change (will affect pitch)
        resampled = torchaudio.functional.resample(
            audio_tensor,
            orig_freq=sample_rate,
            new_freq=new_sample_rate
        )
        
        # Resample back to original rate to maintain expected sample rate
        return torchaudio.functional.resample(
            resampled,
            orig_freq=new_sample_rate, 
            new_freq=sample_rate
        )
        
    except ImportError:
        raise ImportError("torchaudio not available")
    except Exception as e:
        raise RuntimeError(f"torchaudio processing failed: {e}")
        
    except ImportError:
        logger.error("Neither librosa nor torchaudio available for speed adjustment")
        return audio_tensor
    except Exception as e:
        logger.error(f"Fallback speed factor application failed: {e}")
        return audio_tensor


def calculate_audio_duration(file_path: Union[str, Path]) -> Optional[float]:
    """
    Calculate audio file duration in seconds using multiple methods
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds or None if calculation fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    try:
        # Try soundfile first (fastest and most reliable)
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            return len(f) / f.samplerate
    except Exception:
        pass
    
    try:
        # Fallback to librosa
        import librosa
        y, sr = librosa.load(str(file_path), sr=None)
        return len(y) / sr
    except Exception:
        pass
    
    try:
        # Fallback to pydub
        from pydub import AudioSegment
        audio = AudioSegment.from_file(str(file_path))
        return len(audio) / 1000.0  # pydub returns milliseconds
    except Exception:
        pass
    
    logger.warning(f"Could not calculate duration for {file_path}")
    return None


def load_voice_metadata(voice_file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load voice metadata from companion JSON file or calculate if missing
    
    Args:
        voice_file_path: Path to voice audio file
    
    Returns:
        Dictionary with voice metadata
    """
    import json
    from datetime import datetime
    
    voice_path = Path(voice_file_path)
    metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
    
    # Try to load existing metadata
    metadata = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load metadata for {voice_path}: {e}")
    
    # Calculate missing metadata
    if not metadata.get('name'):
        metadata['name'] = voice_path.stem
    
    if not metadata.get('duration_seconds'):
        metadata['duration_seconds'] = calculate_audio_duration(voice_path)
    
    if not metadata.get('file_size_bytes'):
        try:
            metadata['file_size_bytes'] = voice_path.stat().st_size
        except Exception:
            metadata['file_size_bytes'] = None
    
    if not metadata.get('format'):
        metadata['format'] = voice_path.suffix.lower().lstrip('.')
    
    if not metadata.get('sample_rate'):
        try:
            import soundfile as sf
            with sf.SoundFile(str(voice_path)) as f:
                metadata['sample_rate'] = f.samplerate
        except Exception:
            metadata['sample_rate'] = None
    
    if not metadata.get('created_date'):
        try:
            created_time = voice_path.stat().st_ctime
            metadata['created_date'] = datetime.fromtimestamp(created_time).isoformat()
        except Exception:
            metadata['created_date'] = None
    
    # Ensure required fields have defaults
    metadata.setdefault('description', f"Voice file: {voice_path.name}")
    metadata.setdefault('tags', [])
    metadata.setdefault('usage_count', 0)
    metadata.setdefault('default_parameters', {})
    
    return metadata


def save_voice_metadata(voice_file_path: Union[str, Path], metadata: Dict[str, Any]) -> bool:
    """
    Save voice metadata to companion JSON file
    
    Args:
        voice_file_path: Path to voice audio file
        metadata: Metadata dictionary to save
    
    Returns:
        True if saved successfully, False otherwise
    """
    import json
    from datetime import datetime
    
    try:
        voice_path = Path(voice_file_path)
        metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
        
        # Update timestamp
        metadata['last_updated'] = datetime.now().isoformat()
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Voice metadata saved: {metadata_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save voice metadata for {voice_file_path}: {e}")
        return False


def update_voice_usage(voice_file_path: Union[str, Path]) -> None:
    """
    Update voice usage statistics
    
    Args:
        voice_file_path: Path to voice audio file
    """
    from datetime import datetime
    
    try:
        metadata = load_voice_metadata(voice_file_path)
        metadata['usage_count'] = metadata.get('usage_count', 0) + 1
        metadata['last_used'] = datetime.now().isoformat()
        save_voice_metadata(voice_file_path, metadata)
    except Exception as e:
        logger.warning(f"Failed to update voice usage for {voice_file_path}: {e}")


def validate_text_length(text: str, max_length: int = 10000) -> bool:
    """Validate text length for TTS generation"""
    return len(text.strip()) > 0 and len(text) <= max_length


def normalize_audio_path(path_input: Union[str, Path]) -> Path:
    """Normalize audio path input to Path object"""
    if isinstance(path_input, str):
        return Path(path_input)
    return path_input


def get_supported_audio_formats() -> List[str]:
    """Get list of supported audio formats"""
    return ["wav", "mp3", "flac"]


def validate_audio_format(format_name: str) -> bool:
    """Validate if audio format is supported"""
    return format_name.lower() in get_supported_audio_formats()


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted and safe"""
    import re
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Check for potentially dangerous URLs (localhost and private IPs)
    dangerous_patterns = [
        r'.*localhost.*',
        r'.*127\.0\.0\.1.*',
        r'.*0\.0\.0\.0.*',
        r'.*192\.168\..*',
        r'.*10\..*',
        r'.*172\.(1[6-9]|2[0-9]|3[0-1])\..*',  # Private IP ranges
    ]
    
    for pattern in dangerous_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return False
    
    return True


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path for safe usage"""
    import os
    
    # Convert to Path and resolve any relative components
    path = Path(file_path)
    
    # Remove any directory traversal attempts
    path_parts = []
    for part in path.parts:
        if part in ('..', '.'):
            continue
        part = sanitize_filename(part)
        path_parts.append(part)
    
    # Reconstruct path using forward slashes (cross-platform)
    if path_parts:
        return '/'.join(path_parts)
    else:
        return "unnamed"


def validate_text_input(text: str) -> tuple[bool, str]:
    """
    Validate and sanitize text input for TTS generation
    Returns (is_valid, sanitized_text)
    """
    if not text or not text.strip():
        return False, ""
    
    text = text.strip()
    
    # Check length
    max_length = 10000  # Could be configurable
    if len(text) > max_length:
        return False, text[:max_length]
    
    # Basic sanitization - remove potential control characters
    import re
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return True, text


def validate_voice_file(file_content: bytes, filename: str) -> tuple[bool, str]:
    """
    Validate uploaded voice file for security and format
    
    Args:
        file_content: File content bytes
        filename: Original filename
    
    Returns:
        (is_valid, error_message)
    """
    # File size validation (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    if len(file_content) > max_size:
        return False, f"File too large: {len(file_content)} bytes (max {max_size})"
    
    # File extension validation
    allowed_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    file_ext = Path(filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file format: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
    
    # Basic file signature validation
    audio_signatures = {
        b'RIFF': 'wav',
        b'fLaC': 'flac', 
        b'OggS': 'ogg',
        b'ID3': 'mp3',
        b'\xff\xfb': 'mp3',
        b'\xff\xf3': 'mp3',
        b'\xff\xf2': 'mp3'
    }
    
    # Check file signature
    signature_found = False
    for sig, format_name in audio_signatures.items():
        if file_content.startswith(sig):
            signature_found = True
            break
    
    if not signature_found:
        return False, "File does not appear to be a valid audio file"
    
    return True, ""


def save_uploaded_voice(file_content: bytes, filename: str, folder_path: Optional[str] = None, 
                       overwrite: bool = False) -> tuple[bool, str, Optional[Path]]:
    """
    Save uploaded voice file to reference_audio directory
    
    Args:
        file_content: File content bytes
        filename: Desired filename
        folder_path: Optional folder organization path
        overwrite: Whether to overwrite existing files
    
    Returns:
        (success, message, saved_path)
    """
    from config import config_manager
    
    # Get reference audio directory
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    
    # Create target directory path
    if folder_path:
        # Sanitize folder path
        folder_path = sanitize_filename(folder_path)
        target_dir = ref_audio_dir / folder_path
    else:
        target_dir = ref_audio_dir
    
    # Ensure directory exists
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Failed to create directory: {e}", None
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    target_path = target_dir / safe_filename
    
    # Check if file exists and overwrite policy
    if target_path.exists() and not overwrite:
        return False, f"Voice file already exists: {safe_filename}. Use overwrite=true to replace.", None
    
    # Save file
    try:
        with open(target_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Voice file saved: {target_path}")
        return True, f"Voice file saved successfully: {safe_filename}", target_path
    except Exception as e:
        logger.error(f"Failed to save voice file: {e}")
        return False, f"Failed to save voice file: {e}", None


def create_voice_metadata_from_upload(voice_path: Path, upload_metadata: dict) -> dict:
    """
    Create comprehensive voice metadata from uploaded file and user input
    
    Args:
        voice_path: Path to saved voice file
        upload_metadata: Metadata from upload request
    
    Returns:
        Complete metadata dictionary
    """
    from datetime import datetime
    
    # Start with calculated metadata
    metadata = load_voice_metadata(voice_path)
    
    # Override with user-provided metadata
    if upload_metadata.get('name'):
        metadata['name'] = upload_metadata['name']
    
    if upload_metadata.get('description'):
        metadata['description'] = upload_metadata['description']
    
    if upload_metadata.get('tags'):
        metadata['tags'] = upload_metadata['tags']
    
    if upload_metadata.get('default_parameters'):
        metadata['default_parameters'] = upload_metadata['default_parameters']
    
    # Set folder path if provided
    if upload_metadata.get('folder_path'):
        metadata['folder_path'] = upload_metadata['folder_path']
    
    # Update timestamps
    metadata['created_date'] = datetime.now().isoformat()
    metadata['last_used'] = None  # Not used yet
    metadata['usage_count'] = 0   # Reset usage count for new upload
    
    return metadata


def scan_generated_files(outputs_dir: Union[str, Path], generation_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan outputs directory for generated files and their metadata
    
    Args:
        outputs_dir: Path to outputs directory
        generation_type: Filter by generation type ('tts', 'vc', 'concat')
    
    Returns:
        List of file metadata dictionaries
    """
    import json
    from datetime import datetime
    
    outputs_path = Path(outputs_dir)
    if not outputs_path.exists():
        return []
    
    files_metadata = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    for audio_file in outputs_path.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            # Look for companion JSON metadata file
            metadata_file = audio_file.with_suffix(audio_file.suffix + '.json')
            
            # Initialize metadata
            metadata = {
                'filename': audio_file.name,
                'generation_type': 'unknown',
                'created_date': None,
                'file_size_bytes': None,
                'duration_seconds': None,
                'format': audio_file.suffix.lower().lstrip('.'),
                'parameters': {},
                'source_files': [],
                'folder_path': None
            }
            
            # Load from companion JSON if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        json_metadata = json.load(f)
                        metadata.update(json_metadata)
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {audio_file}: {e}")
            
            # Calculate missing metadata
            try:
                if not metadata['file_size_bytes']:
                    metadata['file_size_bytes'] = audio_file.stat().st_size
                
                if not metadata['created_date']:
                    created_time = audio_file.stat().st_ctime
                    metadata['created_date'] = datetime.fromtimestamp(created_time).isoformat()
                
                if not metadata['duration_seconds']:
                    metadata['duration_seconds'] = calculate_audio_duration(audio_file)
                
                # Calculate folder path relative to outputs directory
                relative_path = audio_file.relative_to(outputs_path)
                if relative_path.parent != Path('.'):
                    metadata['folder_path'] = str(relative_path.parent)
                
                # Infer generation type from filename pattern if not set
                if metadata['generation_type'] == 'unknown':
                    filename_lower = audio_file.name.lower()
                    if filename_lower.startswith('tts_'):
                        metadata['generation_type'] = 'tts'
                    elif filename_lower.startswith('vc_'):
                        metadata['generation_type'] = 'vc'
                    elif filename_lower.startswith('concat_'):
                        metadata['generation_type'] = 'concat'
                    else:
                        metadata['generation_type'] = 'unknown'
                
            except Exception as e:
                logger.warning(f"Failed to calculate metadata for {audio_file}: {e}")
            
            # Apply generation type filter
            if generation_type and metadata['generation_type'] != generation_type:
                continue
            
            files_metadata.append(metadata)
    
    # Sort by creation date (newest first)
    files_metadata.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    
    return files_metadata


def find_files_by_names(outputs_dir: Union[str, Path], filenames: List[str]) -> List[Dict[str, Any]]:
    """
    Find specific files by their names in outputs directory
    
    Args:
        outputs_dir: Path to outputs directory
        filenames: List of filenames to find
    
    Returns:
        List of found file metadata dictionaries
    """
    outputs_path = Path(outputs_dir)
    if not outputs_path.exists():
        return []
    
    found_files = []
    
    for filename in filenames:
        # Try to find the file
        matches = list(outputs_path.rglob(filename))
        
        if matches:
            # Use the first match
            audio_file = matches[0]
            
            # Get metadata for this file
            file_metadata = scan_generated_files(outputs_dir)
            for metadata in file_metadata:
                if metadata['filename'] == filename:
                    found_files.append(metadata)
                    break
    
    return found_files


def delete_voice_file(voice_filename: str) -> tuple[bool, str, List[str]]:
    """
    Delete a voice file and its metadata
    
    Args:
        voice_filename: Name of voice file to delete
    
    Returns:
        (success, message, deleted_files_list)
    """
    from config import config_manager
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    deleted_files = []
    
    # Find the voice file
    matches = list(ref_audio_dir.rglob(voice_filename))
    
    if not matches:
        return False, f"Voice file not found: {voice_filename}", []
    
    voice_path = matches[0]  # Use first match
    
    try:
        # Delete the audio file
        if voice_path.exists():
            voice_path.unlink()
            deleted_files.append(str(voice_path.name))
            logger.info(f"Deleted voice file: {voice_path}")
        
        # Delete companion metadata file if exists
        metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
        if metadata_path.exists():
            metadata_path.unlink()
            deleted_files.append(str(metadata_path.name))
            logger.info(f"Deleted metadata file: {metadata_path}")
        
        return True, f"Voice '{voice_filename}' deleted successfully", deleted_files
        
    except Exception as e:
        logger.error(f"Failed to delete voice {voice_filename}: {e}")
        return False, f"Failed to delete voice: {e}", deleted_files


def bulk_delete_voices(folder: Optional[str] = None, tag: Optional[str] = None, 
                      search: Optional[str] = None, filenames: Optional[List[str]] = None) -> tuple[bool, str, List[str]]:
    """
    Bulk delete voices based on criteria
    
    Args:
        folder: Filter by folder path
        tag: Filter by tag
        search: Search term
        filenames: Specific filenames to delete
    
    Returns:
        (success, message, deleted_files_list)
    """
    from config import config_manager
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if not ref_audio_dir.exists():
        return False, "Reference audio directory not found", []
    
    deleted_files = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Handle specific filenames
    if filenames:
        for filename in filenames:
            success, message, files = delete_voice_file(filename)
            if success:
                deleted_files.extend(files)
        
        total_deleted = len([f for f in deleted_files if not f.endswith('.json')])
        return True, f"Deleted {total_deleted} voice files", deleted_files
    
    # Scan for files matching criteria
    voices_to_delete = []
    
    for audio_file in ref_audio_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            # Load metadata for filtering
            metadata = load_voice_metadata(audio_file)
            
            # Apply filters
            should_delete = True
            
            if folder:
                relative_path = audio_file.relative_to(ref_audio_dir)
                file_folder = str(relative_path.parent) if relative_path.parent != Path('.') else None
                if file_folder != folder:
                    should_delete = False
            
            if tag and should_delete:
                file_tags = metadata.get('tags', [])
                if tag not in file_tags:
                    should_delete = False
            
            if search and should_delete:
                search_lower = search.lower()
                searchable_text = f"{metadata.get('name', '')} {metadata.get('description', '')} {' '.join(metadata.get('tags', []))}"
                if search_lower not in searchable_text.lower():
                    should_delete = False
            
            if should_delete:
                voices_to_delete.append(audio_file.name)
    
    # Delete matching voices
    for voice_filename in voices_to_delete:
        success, message, files = delete_voice_file(voice_filename)
        if success:
            deleted_files.extend(files)
    
    total_deleted = len([f for f in deleted_files if not f.endswith('.json')])
    return True, f"Deleted {total_deleted} voice files matching criteria", deleted_files


def update_voice_metadata_only(voice_filename: str, metadata_updates: dict) -> tuple[bool, str, dict]:
    """
    Update voice metadata without changing the audio file
    
    Args:
        voice_filename: Name of voice file
        metadata_updates: Dictionary of metadata updates
    
    Returns:
        (success, message, updated_metadata)
    """
    from config import config_manager
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    
    # Find the voice file
    matches = list(ref_audio_dir.rglob(voice_filename))
    
    if not matches:
        return False, f"Voice file not found: {voice_filename}", {}
    
    voice_path = matches[0]
    
    try:
        # Load existing metadata
        current_metadata = load_voice_metadata(voice_path)
        
        # Apply updates (only for non-None values)
        for key, value in metadata_updates.items():
            if value is not None:
                current_metadata[key] = value
        
        # Update timestamp
        from datetime import datetime
        current_metadata['last_updated'] = datetime.now().isoformat()
        
        # Save updated metadata
        save_voice_metadata(voice_path, current_metadata)
        
        return True, f"Metadata updated for '{voice_filename}'", current_metadata
        
    except Exception as e:
        logger.error(f"Failed to update metadata for {voice_filename}: {e}")
        return False, f"Failed to update metadata: {e}", {}


def get_voice_folder_structure() -> dict:
    """
    Get the folder structure of the voice library
    
    Returns:
        Dictionary with folder structure information
    """
    from config import config_manager
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if not ref_audio_dir.exists():
        return {"folders": [], "total_folders": 0, "total_voices": 0}
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    folder_info = {}
    total_voices = 0
    
    # First, scan all directories (including empty ones)
    for item in ref_audio_dir.rglob("*"):
        if item.is_dir():
            # Get relative folder path
            relative_path = item.relative_to(ref_audio_dir)
            folder_path = str(relative_path) if relative_path != Path('.') else ""
            
            if folder_path and folder_path not in folder_info:
                folder_info[folder_path] = {
                    "path": folder_path,
                    "voice_count": 0,
                    "subfolders": set()
                }
    
    # Add root folder if it doesn't exist
    if "" not in folder_info:
        folder_info[""] = {
            "path": "",
            "voice_count": 0,
            "subfolders": set()
        }
    
    # Now scan all audio files and count them in their respective folders
    for audio_file in ref_audio_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            total_voices += 1
            
            # Get relative folder path
            relative_path = audio_file.relative_to(ref_audio_dir)
            folder_path = str(relative_path.parent) if relative_path.parent != Path('.') else ""
            
            # Ensure folder exists in our tracking (should already exist from directory scan)
            if folder_path not in folder_info:
                folder_info[folder_path] = {
                    "path": folder_path,
                    "voice_count": 0,
                    "subfolders": set()
                }
            
            folder_info[folder_path]["voice_count"] += 1
    
    # Calculate subfolders for each folder
    all_folders = list(folder_info.keys())
    
    for folder_path in all_folders:
        for other_folder in all_folders:
            if other_folder != folder_path:
                # Check if other_folder is a direct subfolder of folder_path
                if folder_path == "":
                    # Root folder - direct subfolders have no "/" in their path
                    if "/" not in other_folder and other_folder != "":
                        folder_info[folder_path]["subfolders"].add(other_folder)
                else:
                    # Check if it's a direct subfolder (not nested deeper)
                    if other_folder.startswith(folder_path + "/"):
                        relative_part = other_folder[len(folder_path + "/"):]
                        if "/" not in relative_part:  # Direct subfolder
                            folder_info[folder_path]["subfolders"].add(relative_part)
    
    # Convert sets to lists and prepare response
    folders = []
    for folder_data in folder_info.values():
        folder_data["subfolders"] = sorted(list(folder_data["subfolders"]))
        folders.append(folder_data)
    
    # Sort folders by path
    folders.sort(key=lambda x: x["path"])
    
    return {
        "folders": folders,
        "total_folders": len(folders),
        "total_voices": total_voices
    }


def concatenate_audio_files(file_paths: List[Path], output_path: Path, 
                          normalize_levels: bool = True, crossfade_ms: int = 0,
                          pause_duration_ms: int = 600, pause_variation_ms: int = 200) -> Dict[str, Any]:
    """
    Concatenate multiple audio files into a single file with natural pauses
    
    Args:
        file_paths: List of paths to audio files to concatenate
        output_path: Output file path
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration in milliseconds
        pause_duration_ms: Base pause duration between clips in milliseconds
        pause_variation_ms: Random variation in pause duration (v) in milliseconds
    
    Returns:
        Dictionary with concatenation metadata
    """
    try:
        from pydub import AudioSegment
        import librosa
        import soundfile as sf
        # random is already imported at module level
    except ImportError as e:
        raise ImportError(f"Required audio library not available: {e}")
    
    start_time = time.time()
    combined_audio = None
    total_duration = 0
    processed_files = []
    total_pause_duration = 0
    
    logger.info(f"Starting concatenation of {len(file_paths)} files with natural pauses")
    logger.info(f"Pause parameters: duration={pause_duration_ms}ms, variation=+/-{pause_variation_ms}ms")
    
    for i, file_path in enumerate(file_paths):
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path.name}")
        
        try:
            # Load audio file using pydub for format flexibility
            audio_segment = AudioSegment.from_file(str(file_path))
            
            # Normalize levels if requested
            if normalize_levels:
                # Normalize to -20dB to prevent clipping
                target_dBFS = -20.0
                change_in_dBFS = target_dBFS - audio_segment.dBFS
                audio_segment = audio_segment.apply_gain(change_in_dBFS)
            
            # Add to combined audio
            if combined_audio is None:
                # First file - no pause before it
                combined_audio = audio_segment
            else:
                # Calculate natural pause duration with variation
                if pause_duration_ms > 0:
                    # Generate random variation within bounds
                    min_pause = max(100, pause_duration_ms - pause_variation_ms)  # Minimum 100ms
                    max_pause = min(3000, pause_duration_ms + pause_variation_ms)  # Maximum 3000ms
                    actual_pause_ms = random.randint(min_pause, max_pause)
                    
                    # Create silence segment
                    pause_segment = AudioSegment.silent(duration=actual_pause_ms)
                    total_pause_duration += actual_pause_ms
                    
                    logger.info(f"Adding {actual_pause_ms}ms natural pause between clips")
                    
                    if crossfade_ms > 0:
                        # Apply crossfade with pause: 
                        # We want: previous_audio -> crossfade with new_audio -> pause -> ready for next
                        # So: crossfade first, then add pause for next iteration
                        combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                        combined_audio = combined_audio + pause_segment
                    else:
                        # Simple concatenation with pause: previous_audio + pause + new_audio
                        combined_audio = combined_audio + pause_segment + audio_segment
                else:
                    # No pause requested, use original behavior
                    if crossfade_ms > 0:
                        combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                    else:
                        combined_audio = combined_audio + audio_segment
            
            duration_seconds = len(audio_segment) / 1000.0
            total_duration += duration_seconds
            processed_files.append({
                "filename": file_path.name,
                "duration_seconds": duration_seconds,
                "size_bytes": file_path.stat().st_size
            })
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise RuntimeError(f"Failed to process audio file {file_path.name}: {e}")
    
    if combined_audio is None:
        raise RuntimeError("No audio content to concatenate")
    
    # Export the combined audio
    logger.info(f"Exporting concatenated audio to: {output_path}")
    
    # Determine format from extension
    file_extension = output_path.suffix.lower()
    
    if file_extension == '.wav':
        combined_audio.export(str(output_path), format="wav")
    elif file_extension == '.mp3':
        combined_audio.export(str(output_path), format="mp3", bitrate="192k")
    elif file_extension == '.flac':
        combined_audio.export(str(output_path), format="flac")
    else:
        # Default to WAV
        combined_audio.export(str(output_path), format="wav")
    
    processing_time = time.time() - start_time
    
    # Calculate final file info
    final_duration = len(combined_audio) / 1000.0
    final_size = output_path.stat().st_size if output_path.exists() else 0
    
    logger.info(f"Concatenation completed in {processing_time:.2f}s")
    logger.info(f"Final audio: {final_duration:.2f}s, {final_size} bytes")
    logger.info(f"Total pause duration: {total_pause_duration/1000:.2f}s")
    
    return {
        "total_duration_seconds": final_duration,
        "file_count": len(file_paths),
        "processing_time_seconds": processing_time,
        "processed_files": processed_files,
        "output_size_bytes": final_size,
        "crossfade_ms": crossfade_ms,
        "normalized": normalize_levels,
        "pause_duration_ms": pause_duration_ms,
        "pause_variation_ms": pause_variation_ms,
        "total_pause_duration_ms": total_pause_duration
    }


def concatenate_with_silence(parsed_items: List[Dict], output_path: Path, 
                           normalize_levels: bool = True, crossfade_ms: int = 0,
                           outputs_dir: Path = None) -> Dict[str, Any]:
    """
    Concatenate audio files and silence segments based on parsed instructions
    
    Args:
        parsed_items: Output from parse_concat_files() containing file and silence instructions
        output_path: Where to save the result
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration between audio segments (not applied to silence)
        outputs_dir: Directory where audio files are located
    
    Returns:
        Metadata about the concatenation process
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required for audio concatenation")
    
    start_time = time.time()
    combined_audio = AudioSegment.empty()
    processing_info = []
    total_duration = 0
    silence_count = 0
    file_count = 0
    last_segment_type = None  # Track the type of the last segment added
    
    logger.info(f"Starting enhanced concatenation with {len(parsed_items)} segments (files and silence)")
    
    for i, item in enumerate(parsed_items):
        if item["type"] == "silence":
            # Generate and add silence segment
            silence_segment = generate_silence_segment(item["duration_ms"])
            combined_audio += silence_segment
            
            silence_count += 1
            duration_seconds = item["duration_ms"] / 1000.0
            total_duration += duration_seconds
            last_segment_type = "silence"
            
            processing_info.append({
                "type": "silence",
                "duration_ms": item["duration_ms"],
                "duration_seconds": duration_seconds,
                "notation": item["source"]
            })
            
            logger.info(f"Added {item['duration_ms']}ms silence segment from notation: {item['source']}")
            
        else:
            # Process audio file
            file_count += 1
            filename = item["source"]
            
            # Resolve file path
            if outputs_dir:
                file_path = outputs_dir / filename
            else:
                file_path = Path(filename)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            logger.info(f"Processing audio file {file_count}: {filename}")
            
            try:
                # Load audio file
                audio_segment = AudioSegment.from_file(str(file_path))
                
                # Normalize levels if requested
                if normalize_levels:
                    target_dBFS = -20.0
                    change_in_dBFS = target_dBFS - audio_segment.dBFS
                    audio_segment = audio_segment.apply_gain(change_in_dBFS)
                
                # Apply crossfade only between consecutive audio segments (not with silence)
                if (crossfade_ms > 0 and 
                    len(combined_audio) > 0 and 
                    last_segment_type == "file"):
                    # Only crossfade if the previous segment was also an audio file
                    combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                    logger.info(f"Applied {crossfade_ms}ms crossfade between audio files")
                else:
                    # No crossfade: either first segment, follows silence, or crossfade disabled
                    combined_audio += audio_segment
                    if crossfade_ms > 0 and last_segment_type == "silence":
                        logger.info(f"Skipped crossfade after silence segment for clean audio start")
                
                duration_seconds = len(audio_segment) / 1000.0
                total_duration += duration_seconds
                last_segment_type = "file"
                
                processing_info.append({
                    "type": "file",
                    "filename": filename,
                    "duration_seconds": duration_seconds,
                    "size_bytes": file_path.stat().st_size
                })
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                raise RuntimeError(f"Failed to process audio file {filename}: {e}")
    
    if len(combined_audio) == 0:
        raise RuntimeError("No audio content to concatenate")
    
    # Export the combined audio
    logger.info(f"Exporting enhanced concatenated audio to: {output_path}")
    
    # Determine format from extension
    file_extension = output_path.suffix.lower()
    
    if file_extension == '.wav':
        combined_audio.export(str(output_path), format="wav")
    elif file_extension == '.mp3':
        combined_audio.export(str(output_path), format="mp3", bitrate="192k")
    elif file_extension == '.flac':
        combined_audio.export(str(output_path), format="flac")
    else:
        # Default to WAV
        combined_audio.export(str(output_path), format="wav")
    
    processing_time = time.time() - start_time
    
    # Calculate final file info
    final_duration = len(combined_audio) / 1000.0
    final_size = output_path.stat().st_size if output_path.exists() else 0
    
    logger.info(f"Enhanced concatenation completed in {processing_time:.2f}s")
    logger.info(f"Final audio: {final_duration:.2f}s, {final_size} bytes")
    logger.info(f"Processed: {file_count} audio files, {silence_count} silence segments")
    
    return {
        "total_duration_seconds": final_duration,
        "file_count": file_count,
        "silence_segments": silence_count,
        "total_segments": len(parsed_items),
        "processing_time_seconds": processing_time,
        "processing_details": processing_info,
        "output_size_bytes": final_size,
        "crossfade_ms": crossfade_ms,
        "normalized": normalize_levels
    }

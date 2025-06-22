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

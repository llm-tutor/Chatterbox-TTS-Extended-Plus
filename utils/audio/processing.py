# utils/audio/processing.py - Audio Processing & Speed Factor Functions

import os
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import torch
import numpy as np

logger = logging.getLogger(__name__)


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


def get_audio_duration(file_path: Path) -> Optional[float]:
    """Get audio file duration in seconds"""
    try:
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            return len(f) / f.samplerate
    except Exception as e:
        logger.warning(f"Could not get duration for {file_path}: {e}")
        return None


def get_audio_duration_ms(audio_path: Path) -> float:
    """
    Get audio file duration in milliseconds
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Duration in milliseconds
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(str(audio_path))
        return len(audio)
    except Exception as e:
        logger.error(f"Error getting duration for {audio_path}: {e}")
        return 0.0

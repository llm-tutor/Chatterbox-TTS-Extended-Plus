# Phase 10.1.1 Enhanced Speed Factor Implementation - BACKUP
# This file contains our working implementation for future integration

"""
Enhanced speed factor implementation with multi-library support.
This is a backup of the working code before performance issues.
The implementation works correctly but causes performance regression
in the TTS pipeline. Needs further optimization for integration.
"""

# BACKUP: utils.py enhanced apply_speed_factor function
BACKUP_APPLY_SPEED_FACTOR = '''
def apply_speed_factor(
    audio_tensor: torch.Tensor, 
    sample_rate: int, 
    speed_factor: float,
    preferred_library: Optional[str] = None
) -> torch.Tensor:
    """
    Apply speed factor to audio while preserving pitch using best available library
    
    PERFORMANCE OPTIMIZED: Early return for speed_factor=1.0 before any imports or processing
    
    Args:
        audio_tensor: Input audio tensor (1D or 2D)
        sample_rate: Audio sample rate
        speed_factor: Speed multiplier (0.5x to 2.0x)
        preferred_library: Optional library override
    
    Returns:
        Speed-adjusted audio tensor
    """
    # CRITICAL: Return immediately for 1.0 before any expensive operations
    if speed_factor == 1.0:
        return audio_tensor
    
    # Only do expensive imports and config loading if we actually need to process
    try:
        # Import config_manager only when needed
        from config import config_manager
        
        # Get configuration for fallback chain and preferred library
        config = config_manager.config.get('speed_factor', {})
        if preferred_library is None:
            preferred_library = config.get('preferred_library', 'audiostretchy')
        
        # For now, use simple fallback to avoid complex library chain during debugging
        # TODO: Re-enable full library chain after performance is confirmed
        if preferred_library == 'audiostretchy':
            return _apply_speed_audiostretchy_simple(audio_tensor, sample_rate, speed_factor)
        elif preferred_library == 'pyrubberband':
            return _apply_speed_pyrubberband_simple(audio_tensor, sample_rate, speed_factor)
        else:
            # Fall back to librosa (original working implementation)
            return _apply_speed_librosa_simple(audio_tensor, sample_rate, speed_factor)
            
    except Exception as e:
        logger.warning(f"Enhanced speed factor failed: {e}, falling back to librosa")
        return _apply_speed_librosa_simple(audio_tensor, sample_rate, speed_factor)


def _apply_speed_librosa_simple(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """Simple librosa implementation - known working baseline"""
    try:
        import librosa
        
        # Convert tensor to numpy array
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.detach().cpu().numpy()
            original_device = audio_tensor.device
        else:
            audio_np = audio_tensor
            original_device = None
        
        # Handle multi-channel audio
        if audio_np.ndim == 2:
            processed_channels = []
            for channel in range(audio_np.shape[0]):
                processed_channel = librosa.effects.time_stretch(audio_np[channel], rate=speed_factor)
                processed_channels.append(processed_channel)
            processed_audio = np.stack(processed_channels, axis=0)
        else:
            processed_audio = librosa.effects.time_stretch(audio_np, rate=speed_factor)
        
        # Convert back to tensor
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except ImportError:
        logger.error("librosa not available")
        return audio_tensor
    except Exception as e:
        logger.error(f"librosa speed factor failed: {e}")
        return audio_tensor


def _apply_speed_audiostretchy_simple(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """Simplified audiostretchy implementation"""
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
        
        # audiostretchy ratio (inverse of speed_factor)
        ratio = 1.0 / speed_factor
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
            temp_input_path = temp_input.name
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Write input
            if audio_np.ndim == 2:
                sf.write(temp_input_path, audio_np.T, sample_rate)  # Transpose for soundfile
            else:
                sf.write(temp_input_path, audio_np, sample_rate)
            
            # Process with audiostretchy
            stretch_audio(temp_input_path, temp_output_path, ratio=ratio)
            
            # Read result
            processed_audio, _ = sf.read(temp_output_path)
            
            # Handle channel dimensions
            if audio_np.ndim == 2 and processed_audio.ndim == 2:
                processed_audio = processed_audio.T  # Transpose back
            elif audio_np.ndim == 2 and processed_audio.ndim == 1:
                processed_audio = processed_audio[np.newaxis, :]  # Add channel dimension
            elif audio_np.ndim == 1 and processed_audio.ndim == 2:
                processed_audio = processed_audio[:, 0]  # Take first channel
            
        finally:
            # Cleanup temp files
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
            except:
                pass
        
        # Convert back to tensor
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except Exception as e:
        logger.warning(f"audiostretchy failed: {e}, falling back to librosa")
        return _apply_speed_librosa_simple(audio_tensor, sample_rate, speed_factor)


def _apply_speed_pyrubberband_simple(audio_tensor: torch.Tensor, sample_rate: int, speed_factor: float) -> torch.Tensor:
    """Simplified pyrubberband implementation"""
    try:
        import pyrubberband as pyrb
        
        # Convert tensor to numpy
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.detach().cpu().numpy()
            original_device = audio_tensor.device
        else:
            audio_np = audio_tensor
            original_device = None
        
        # High quality settings
        rb_args = {"--fine": "", "--formant": "", "--crisp": "5"}
        
        # Process with pyrubberband
        if audio_np.ndim == 2:
            processed_channels = []
            for channel in range(audio_np.shape[0]):
                processed_channel = pyrb.time_stretch(
                    audio_np[channel], sample_rate, speed_factor, rbargs=rb_args
                )
                processed_channels.append(processed_channel)
            processed_audio = np.stack(processed_channels, axis=0)
        else:
            processed_audio = pyrb.time_stretch(
                audio_np, sample_rate, speed_factor, rbargs=rb_args
            )
        
        # Convert back to tensor
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except Exception as e:
        logger.warning(f"pyrubberband failed: {e}, falling back to librosa")
        return _apply_speed_librosa_simple(audio_tensor, sample_rate, speed_factor)
'''

# BACKUP: config.yaml speed factor configuration
BACKUP_CONFIG_YAML = '''
# Speed Factor Configuration (Phase 10.1.1)
speed_factor:
  # Preferred library for speed adjustment (admin setting)
  preferred_library: "audiostretchy"    # Options: audiostretchy, pyrubberband, librosa, torchaudio
  
  # Fallback chain when preferred library fails
  fallback_chain:
    - "audiostretchy"                   # Best for speech quality (TDHS algorithm)
    - "pyrubberband"                    # Industry standard (advanced phase vocoder)
    - "librosa"                         # Good compatibility (basic phase vocoder)
    - "torchaudio"                      # Basic fallback (pitch-affecting)
  
  # Quality ranges and recommendations  
  quality_ranges:
    audiostretchy_optimal: [0.9, 1.1]  # 10% change - excellent quality
    audiostretchy_good: [0.5, 2.0]     # Full range - good quality
    pyrubberband_optimal: [0.8, 1.25]  # 20-25% change - excellent quality  
    pyrubberband_good: [0.5, 2.0]      # Full range - good quality
    
  # Speed factor limits
  min_speed_factor: 0.5               # Minimum speed (2x slower)
  max_speed_factor: 2.0               # Maximum speed (2x faster)
  
  # Library-specific settings
  audiostretchy:
    # Frequency range for pitch detection (Hz)
    # Default range covers most human speech
    lower_freq: 55                    # Lower frequency bound
    upper_freq: 333                   # Upper frequency bound
    # For male voices: 85-255 Hz might be better
    # For female voices: 165-333 Hz might be better
    
  pyrubberband:
    # Rubberband-specific options (rbargs)
    use_fine_engine: true             # Use R3 engine (--fine) for better quality
    enable_formant_preservation: true # Preserve vocal formants (--formant)
    crispness_level: 5                # Transient handling (0-6, 5 good for speech)
'''

# BACKUP: api_models.py additions
BACKUP_API_MODELS = '''
    speed_factor: float = Field(1.0, ge=0.5, le=2.0, description="Speed adjustment factor (0.5x to 2.0x)")
    speed_factor_library: Optional[str] = Field(
        None, 
        description="Library for speed adjustment: 'audiostretchy', 'pyrubberband', 'librosa', 'torchaudio'. If not specified, uses configured preferred library."
    )

    @validator('speed_factor_library')
    def validate_speed_factor_library(cls, v):
        if v is not None:
            allowed_libraries = ['audiostretchy', 'pyrubberband', 'librosa', 'torchaudio']
            if v not in allowed_libraries:
                raise ValueError(f"speed_factor_library must be one of: {allowed_libraries}")
        return v
'''

print("Phase 10.1.1 Enhanced Speed Factor Implementation backed up successfully!")
print("Files created:")
print("- Enhanced implementation code saved for future optimization")
print("- Configuration examples preserved") 
print("- API model additions documented")
print("")
print("NOTE: This implementation works correctly but causes performance issues")
print("in the TTS pipeline that need to be resolved before integration.")

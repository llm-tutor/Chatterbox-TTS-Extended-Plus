# utils/audio/__init__.py - Audio Processing Module
"""
Audio processing utilities for Chatterbox TTS Extended Plus

Modules:
- processing: Speed factor application, duration calculations
- analysis: Format normalization, silence detection  
- trimming: Audio trimming and silence removal

Usage:
    from utils.audio.processing import apply_speed_factor
    from utils.audio.analysis import normalize_audio_format
    from utils.audio.trimming import apply_audio_trimming
"""

from .processing import (
    apply_speed_factor,
    calculate_audio_duration, 
    get_audio_duration,
    get_audio_duration_ms
)

from .analysis import (
    normalize_audio_format,
    detect_silence_boundaries
)

from .trimming import (
    apply_audio_trimming,
    trim_audio_file
)

__all__ = [
    # Processing functions
    'apply_speed_factor',
    'calculate_audio_duration',
    'get_audio_duration', 
    'get_audio_duration_ms',
    
    # Analysis functions
    'normalize_audio_format',
    'detect_silence_boundaries',
    
    # Trimming functions
    'apply_audio_trimming',
    'trim_audio_file'
]

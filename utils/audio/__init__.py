# utils/audio/__init__.py - Audio Processing Module

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
    'apply_speed_factor',
    'calculate_audio_duration',
    'get_audio_duration', 
    'get_audio_duration_ms',
    'normalize_audio_format',
    'detect_silence_boundaries',
    'apply_audio_trimming',
    'trim_audio_file'
]

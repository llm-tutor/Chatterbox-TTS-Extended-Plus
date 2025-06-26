# utils/concatenation/__init__.py - Concatenation Module

from .parsing import (
    parse_concat_files,
    generate_silence_segment,
    determine_gap_type,
    generate_natural_pause_duration
)

from .basic import concatenate_audio_files

# Import advanced concatenation functions from local advanced module
from .advanced import (
    concatenate_with_silence,
    concatenate_with_trimming,
    concatenate_with_mixed_sources
)

__all__ = [
    'parse_concat_files', 'generate_silence_segment', 'determine_gap_type',
    'generate_natural_pause_duration', 'concatenate_audio_files',
    'concatenate_with_silence', 'concatenate_with_trimming', 
    'concatenate_with_mixed_sources'
]

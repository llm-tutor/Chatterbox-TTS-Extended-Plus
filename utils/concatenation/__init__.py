# utils/concatenation/__init__.py - Audio Concatenation Module  
"""
Audio concatenation utilities for Chatterbox TTS Extended Plus

Modules:
- parsing: Parse concatenation instructions and generate silence
- basic: Basic audio file concatenation
- advanced: Advanced concatenation with trimming, silence, mixed sources

Usage:
    from utils.concatenation.basic import concatenate_audio_files
    from utils.concatenation.advanced import concatenate_with_trimming
    from utils.concatenation.parsing import parse_concat_files
"""

from .parsing import (
    parse_concat_files,
    generate_silence_segment,
    determine_gap_type,
    generate_natural_pause_duration
)

from .basic import concatenate_audio_files

from .advanced import (
    concatenate_with_silence,
    concatenate_with_trimming,
    concatenate_with_mixed_sources
)

__all__ = [
    # Parsing functions
    'parse_concat_files', 
    'generate_silence_segment', 
    'determine_gap_type',
    'generate_natural_pause_duration',
    
    # Basic concatenation
    'concatenate_audio_files',
    
    # Advanced concatenation
    'concatenate_with_silence', 
    'concatenate_with_trimming', 
    'concatenate_with_mixed_sources'
]

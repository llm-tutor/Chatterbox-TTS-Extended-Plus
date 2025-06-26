# utils/concatenation/__init__.py - Concatenation Module

from .parsing import (
    parse_concat_files,
    generate_silence_segment,
    determine_gap_type,
    generate_natural_pause_duration
)

from .basic import concatenate_audio_files

# Import advanced concatenation functions from original utils for now
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils_original import (
        concatenate_with_silence,
        concatenate_with_trimming,
        concatenate_with_mixed_sources
    )
except ImportError:
    def placeholder_function(*args, **kwargs):
        raise NotImplementedError("Function not yet migrated to new utils structure")
    
    concatenate_with_silence = placeholder_function
    concatenate_with_trimming = placeholder_function
    concatenate_with_mixed_sources = placeholder_function

__all__ = [
    'parse_concat_files', 'generate_silence_segment', 'determine_gap_type',
    'generate_natural_pause_duration', 'concatenate_audio_files',
    'concatenate_with_silence', 'concatenate_with_trimming', 
    'concatenate_with_mixed_sources'
]

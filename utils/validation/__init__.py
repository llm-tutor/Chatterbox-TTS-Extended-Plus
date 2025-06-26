# utils/validation/__init__.py - Input Validation Module

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils_original import (
        validate_text_length,
        validate_text_input,
        validate_audio_format,
        validate_url,
        is_url,
        get_supported_audio_formats
    )
except ImportError:
    def placeholder_function(*args, **kwargs):
        raise NotImplementedError("Function not yet migrated to new utils structure")
    
    validate_text_length = placeholder_function
    validate_text_input = placeholder_function
    validate_audio_format = placeholder_function
    validate_url = placeholder_function
    is_url = placeholder_function
    get_supported_audio_formats = placeholder_function

__all__ = [
    'validate_text_length', 'validate_text_input', 'validate_audio_format', 
    'validate_url', 'is_url', 'get_supported_audio_formats'
]

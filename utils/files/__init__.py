# utils/files/__init__.py - File Operations Module

# For now, import from original utils_original.py for backward compatibility
import sys
from pathlib import Path

# Add the project root to import the original utils
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils_original import (
        generate_unique_filename,
        generate_enhanced_filename, 
        sanitize_filename,
        sanitize_file_path,
        normalize_audio_path,
        validate_audio_file,
        get_file_size,
        ensure_directory_exists,
        cleanup_old_files
    )
except ImportError:
    # Placeholder functions if original is not available
    def placeholder_function(*args, **kwargs):
        raise NotImplementedError("Function not yet migrated to new utils structure")
    
    generate_unique_filename = placeholder_function
    generate_enhanced_filename = placeholder_function
    sanitize_filename = placeholder_function
    sanitize_file_path = placeholder_function
    normalize_audio_path = placeholder_function
    validate_audio_file = placeholder_function
    get_file_size = placeholder_function
    ensure_directory_exists = placeholder_function
    cleanup_old_files = placeholder_function

__all__ = [
    'generate_unique_filename',
    'generate_enhanced_filename', 
    'sanitize_filename',
    'sanitize_file_path',
    'normalize_audio_path',
    'validate_audio_file',
    'get_file_size',
    'ensure_directory_exists',
    'cleanup_old_files'
]

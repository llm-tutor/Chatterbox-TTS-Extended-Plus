# utils/files/__init__.py - File Operations Module
"""
File operations utilities for Chatterbox TTS Extended Plus

Modules:
- naming: Filename generation, sanitization, and enhancement
- operations: File validation, size checking, directory management
- paths: Path normalization and sanitization

Usage:
    from utils.files.naming import generate_enhanced_filename
    from utils.files.operations import validate_audio_file
    from utils.files.paths import sanitize_file_path
"""

from .naming import (
    generate_unique_filename,
    generate_enhanced_filename, 
    sanitize_filename,
    sanitize_file_path
)

from .operations import (
    validate_audio_file,
    get_file_size,
    ensure_directory_exists,
    cleanup_old_files
)

from .paths import (
    get_audio_duration,
    normalize_audio_path
)

__all__ = [
    # Naming functions
    'generate_unique_filename',
    'generate_enhanced_filename', 
    'sanitize_filename',
    'sanitize_file_path',
    
    # File operations
    'validate_audio_file',
    'get_file_size',
    'ensure_directory_exists',
    'cleanup_old_files',
    
    # Path operations
    'get_audio_duration',
    'normalize_audio_path'
]

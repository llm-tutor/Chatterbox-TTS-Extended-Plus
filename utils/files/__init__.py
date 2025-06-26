# utils/files/__init__.py - File Operations Module
"""
File operations utilities for Chatterbox TTS Extended Plus

Modules:
- naming: Filename and path generation, sanitization, and enhancement
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
    normalize_audio_path,
    sanitize_file_path
)

from .operations import (
    validate_audio_file,
    get_file_size,
    ensure_directory_exists,
    cleanup_old_files
)

__all__ = [
    # Naming functions
    'generate_unique_filename',
    'generate_enhanced_filename', 
    'sanitize_filename',
    'normalize_audio_path',
    'sanitize_file_path',
    
    # File operations
    'validate_audio_file',
    'get_file_size',
    'ensure_directory_exists',
    'cleanup_old_files',
]

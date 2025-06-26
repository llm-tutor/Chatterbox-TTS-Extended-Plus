# utils/__init__.py - Backward Compatibility Layer for Utils Refactoring

# Audio processing
from .audio import (
    apply_speed_factor, 
    calculate_audio_duration, 
    get_audio_duration,
    get_audio_duration_ms,
    normalize_audio_format,
    detect_silence_boundaries,
    apply_audio_trimming,
    trim_audio_file
)

# Concatenation
from .concatenation import (
    parse_concat_files,
    generate_silence_segment,
    determine_gap_type,
    generate_natural_pause_duration,
    concatenate_audio_files,
    concatenate_with_silence,
    concatenate_with_trimming,
    concatenate_with_mixed_sources
)

# File operations
from .files import (
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

# Voice management
from .voice import (
    load_voice_metadata,
    save_voice_metadata,
    update_voice_usage,
    create_voice_metadata_from_upload,
    validate_voice_file,
    save_uploaded_voice,
    delete_voice_file,
    bulk_delete_voices,
    update_voice_metadata_only,
    get_voice_folder_structure
)

# Generated content management
from .outputs import (
    save_generation_metadata,
    scan_generated_files,
    find_files_by_names
)

# Input validation
from .validation import (
    validate_text_length,
    validate_text_input,
    validate_audio_format,
    validate_url,
    is_url,
    get_supported_audio_formats
)

# Formatting
from .formatting import format_file_size

# Ensure all original imports continue to work
__all__ = [
    # Audio processing
    'apply_speed_factor', 'calculate_audio_duration', 'get_audio_duration', 
    'get_audio_duration_ms', 'normalize_audio_format', 'detect_silence_boundaries',
    'trim_audio_file', 'apply_audio_trimming',
    
    # Concatenation
    'concatenate_audio_files', 'concatenate_with_silence', 'concatenate_with_trimming',
    'concatenate_with_mixed_sources', 'parse_concat_files', 'generate_silence_segment',
    'determine_gap_type', 'generate_natural_pause_duration',
    
    # File management  
    'generate_unique_filename', 'generate_enhanced_filename', 'sanitize_filename',
    'sanitize_file_path', 'normalize_audio_path', 'validate_audio_file',
    'get_file_size', 'ensure_directory_exists', 'cleanup_old_files',
    
    # Voice management
    'load_voice_metadata', 'save_voice_metadata', 'update_voice_usage',
    'create_voice_metadata_from_upload', 'validate_voice_file', 'save_uploaded_voice',
    'delete_voice_file', 'bulk_delete_voices', 'update_voice_metadata_only',
    'get_voice_folder_structure',
    
    # Output management
    'save_generation_metadata', 'scan_generated_files', 'find_files_by_names',
    
    # Validation
    'validate_text_length', 'validate_text_input', 'validate_audio_format', 
    'validate_url', 'is_url', 'get_supported_audio_formats',
    
    # Formatting
    'format_file_size'
]

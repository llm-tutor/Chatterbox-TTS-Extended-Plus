# utils/voice/__init__.py - Voice Management Module
"""
Voice management utilities for Chatterbox TTS Extended Plus

Modules:
- metadata: Voice metadata loading, saving, and usage tracking
- management: Voice file validation, upload, deletion, and updates
- organization: Bulk operations and folder structure management

Usage:
    from utils.voice.metadata import load_voice_metadata
    from utils.voice.management import validate_voice_file
    from utils.voice.organization import bulk_delete_voices
"""

from .metadata import (
    load_voice_metadata,
    save_voice_metadata,
    update_voice_usage,
    create_voice_metadata_from_upload
)

from .management import (
    validate_voice_file,
    save_uploaded_voice,
    delete_voice_file,
    update_voice_metadata_only
)

from .organization import (
    bulk_delete_voices,
    get_voice_folder_structure
)

__all__ = [
    # Metadata functions
    'load_voice_metadata',
    'save_voice_metadata',
    'update_voice_usage',
    'create_voice_metadata_from_upload',
    
    # Management functions
    'validate_voice_file',
    'save_uploaded_voice',
    'delete_voice_file',
    'update_voice_metadata_only',
    
    # Organization functions
    'bulk_delete_voices',
    'get_voice_folder_structure'
]

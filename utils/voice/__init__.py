# utils/voice/__init__.py - Voice Management Module

# For now, import from original utils_original.py for backward compatibility
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils_original import (
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
except ImportError:
    def placeholder_function(*args, **kwargs):
        raise NotImplementedError("Function not yet migrated to new utils structure")
    
    load_voice_metadata = placeholder_function
    save_voice_metadata = placeholder_function
    update_voice_usage = placeholder_function
    create_voice_metadata_from_upload = placeholder_function
    validate_voice_file = placeholder_function
    save_uploaded_voice = placeholder_function
    delete_voice_file = placeholder_function
    bulk_delete_voices = placeholder_function
    update_voice_metadata_only = placeholder_function
    get_voice_folder_structure = placeholder_function

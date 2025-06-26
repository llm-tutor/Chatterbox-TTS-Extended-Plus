# utils/voice/organization.py - Voice Organization and Bulk Operations

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from config import config_manager
from .metadata import load_voice_metadata
from .management import delete_voice_file

logger = logging.getLogger(__name__)


def bulk_delete_voices(folder: Optional[str] = None, tag: Optional[str] = None, 
                      search: Optional[str] = None, filenames: Optional[List[str]] = None) -> Tuple[bool, str, List[str]]:
    """
    Bulk delete voices based on criteria
    
    Args:
        folder: Filter by folder path
        tag: Filter by tag
        search: Search term
        filenames: Specific filenames to delete
    
    Returns:
        (success, message, deleted_files_list)
    """
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if not ref_audio_dir.exists():
        return False, "Reference audio directory not found", []
    
    deleted_files = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Handle specific filenames
    if filenames:
        for filename in filenames:
            success, message, files = delete_voice_file(filename)
            if success:
                deleted_files.extend(files)
        
        total_deleted = len([f for f in deleted_files if not f.endswith('.json')])
        return True, f"Deleted {total_deleted} voice files", deleted_files
    
    # Scan for files matching criteria
    voices_to_delete = []
    
    for audio_file in ref_audio_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            # Load metadata for filtering
            metadata = load_voice_metadata(audio_file)
            
            # Apply filters
            should_delete = True
            
            if folder:
                relative_path = audio_file.relative_to(ref_audio_dir)
                file_folder = str(relative_path.parent) if relative_path.parent != Path('.') else None
                if file_folder != folder:
                    should_delete = False
            
            if tag and should_delete:
                file_tags = metadata.get('tags', [])
                if tag not in file_tags:
                    should_delete = False
            
            if search and should_delete:
                search_lower = search.lower()
                name_match = search_lower in metadata.get('name', '').lower()
                desc_match = search_lower in metadata.get('description', '').lower()
                filename_match = search_lower in audio_file.name.lower()
                
                if not (name_match or desc_match or filename_match):
                    should_delete = False
            
            if should_delete:
                voices_to_delete.append(audio_file.name)
    
    # Delete matching voices
    for filename in voices_to_delete:
        success, message, files = delete_voice_file(filename)
        if success:
            deleted_files.extend(files)
    
    total_deleted = len([f for f in deleted_files if not f.endswith('.json')])
    return True, f"Deleted {total_deleted} voice files", deleted_files


def get_voice_folder_structure() -> Dict[str, Any]:
    """
    Get the folder structure of voice files in reference_audio directory
    
    Returns:
        Dictionary representing folder structure with file counts
    """
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if not ref_audio_dir.exists():
        return {"error": "Reference audio directory not found"}
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    folder_structure = {}
    
    for audio_file in ref_audio_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            relative_path = audio_file.relative_to(ref_audio_dir)
            
            if relative_path.parent == Path('.'):
                # Root level file
                folder_key = "root"
            else:
                # File in subfolder
                folder_key = str(relative_path.parent)
            
            if folder_key not in folder_structure:
                folder_structure[folder_key] = {
                    "count": 0,
                    "files": []
                }
            
            folder_structure[folder_key]["count"] += 1
            folder_structure[folder_key]["files"].append(audio_file.name)
    
    return folder_structure

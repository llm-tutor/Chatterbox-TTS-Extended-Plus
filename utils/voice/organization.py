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
        Dictionary with 'folders' list and summary statistics
    """
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if not ref_audio_dir.exists():
        return {
            "folders": [],
            "total_folders": 0,
            "total_voices": 0
        }
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    folder_data = {}
    
    # Scan all directories
    for path in ref_audio_dir.rglob("*"):
        if path.is_dir():
            relative_path = path.relative_to(ref_audio_dir)
            folder_path = str(relative_path) if relative_path != Path('.') else "root"
            
            if folder_path not in folder_data:
                folder_data[folder_path] = {
                    "voice_count": 0,
                    "subfolders": set()
                }
    
    # Count voices and track folder relationships
    total_voices = 0
    for audio_file in ref_audio_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            relative_path = audio_file.relative_to(ref_audio_dir)
            
            if relative_path.parent == Path('.'):
                # Root level file
                folder_path = "root"
            else:
                # File in subfolder
                folder_path = str(relative_path.parent)
            
            # Ensure folder exists in data
            if folder_path not in folder_data:
                folder_data[folder_path] = {
                    "voice_count": 0,
                    "subfolders": set()
                }
            
            folder_data[folder_path]["voice_count"] += 1
            total_voices += 1
            
            # Track parent-child relationships
            path_parts = Path(folder_path).parts if folder_path != "root" else []
            for i in range(len(path_parts)):
                parent_path = str(Path(*path_parts[:i])) if i > 0 else "root"
                if i < len(path_parts) - 1:
                    child_path = str(Path(*path_parts[:i+1]))
                    if parent_path in folder_data:
                        folder_data[parent_path]["subfolders"].add(child_path)
    
    # Build response format
    folders = []
    for folder_path, data in folder_data.items():
        folders.append({
            "path": folder_path,
            "voice_count": data["voice_count"],
            "subfolders": sorted(list(data["subfolders"]))
        })
    
    # Sort folders by path
    folders.sort(key=lambda x: (x["path"] != "root", x["path"]))
    
    return {
        "folders": folders,
        "total_folders": len(folders),
        "total_voices": total_voices
    }

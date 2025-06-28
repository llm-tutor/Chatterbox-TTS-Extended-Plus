# utils/vc_inputs/folders.py - VC Inputs Directory Folder Structure

import logging
from pathlib import Path
from typing import Dict, Any

from config import config_manager

logger = logging.getLogger(__name__)


def get_vc_inputs_folder_structure() -> Dict[str, Any]:
    """
    Get the folder structure of VC input files in vc_inputs directory
    
    Returns:
        Dictionary with 'folders' list and summary statistics
    """
    vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
    if not vc_inputs_dir.exists():
        return {
            "folders": [],
            "total_folders": 0,
            "total_voices": 0  # Reusing field name for consistency with API model
        }
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    folder_data = {}
    
    # Scan all directories
    for path in vc_inputs_dir.rglob("*"):
        if path.is_dir():
            relative_path = path.relative_to(vc_inputs_dir)
            folder_path = str(relative_path) if relative_path != Path('.') else "root"
            
            if folder_path not in folder_data:
                folder_data[folder_path] = {
                    "voice_count": 0,  # Reusing field name for file count
                    "subfolders": set()
                }
    
    # Count audio files and track folder relationships
    total_files = 0
    for audio_file in vc_inputs_dir.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            relative_path = audio_file.relative_to(vc_inputs_dir)
            
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
            total_files += 1
            
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
        "total_voices": total_files
    }

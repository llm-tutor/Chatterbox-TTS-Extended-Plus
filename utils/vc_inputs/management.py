# utils/vc_inputs/management.py - VC Input Files Management

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

from config import config_manager

logger = logging.getLogger(__name__)


def scan_vc_input_files(vc_inputs_dir: Union[str, Path], folder: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan vc_inputs directory for audio files and their metadata
    
    Args:
        vc_inputs_dir: Path to vc_inputs directory
        folder: Filter by folder path within vc_inputs directory
        
    Returns:
        List of file metadata dictionaries
    """
    from ..audio.processing import calculate_audio_duration
    
    vc_inputs_path = Path(vc_inputs_dir)
    if not vc_inputs_path.exists():
        return []
    
    files_metadata = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    for audio_file in vc_inputs_path.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            # Look for companion JSON metadata file
            metadata_file = audio_file.with_suffix(audio_file.suffix + '.json')
            
            # Initialize metadata
            metadata = {
                'filename': audio_file.name,
                'created_date': None,
                'file_size_bytes': None,
                'duration_seconds': None,
                'format': audio_file.suffix.lower().lstrip('.'),
                'text': None,
                'folder_path': None
            }
            
            # Load from companion JSON if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        json_metadata = json.load(f)
                        if 'text' in json_metadata:
                            metadata['text'] = json_metadata['text']
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {audio_file}: {e}")
            
            # Calculate missing metadata
            try:
                if not metadata['file_size_bytes']:
                    metadata['file_size_bytes'] = audio_file.stat().st_size
                
                if not metadata['created_date']:
                    created_time = audio_file.stat().st_ctime
                    metadata['created_date'] = datetime.fromtimestamp(created_time).isoformat()
                
                # Only calculate duration for non-empty files
                if not metadata['duration_seconds']:
                    if metadata['file_size_bytes'] > 0:
                        metadata['duration_seconds'] = calculate_audio_duration(audio_file)
                    else:
                        metadata['duration_seconds'] = 0.0
                        logger.warning(f"Skipping duration calculation for empty file: {audio_file}")
                
                # Calculate folder path relative to vc_inputs directory
                relative_path = audio_file.relative_to(vc_inputs_path)
                if relative_path.parent != Path('.'):
                    metadata['folder_path'] = str(relative_path.parent)
                
            except Exception as e:
                logger.warning(f"Failed to calculate metadata for {audio_file}: {e}")
            
            # Apply folder filter
            if folder and metadata.get('folder_path') != folder:
                continue
            
            files_metadata.append(metadata)
    
    # Sort by creation date (newest first)
    files_metadata.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    
    return files_metadata


def find_vc_input_files_by_names(vc_inputs_dir: Union[str, Path], filenames: List[str]) -> List[Dict[str, Any]]:
    """
    Find specific VC input files by their names
    
    Args:
        vc_inputs_dir: Path to vc_inputs directory
        filenames: List of filenames to find
        
    Returns:
        List of found file metadata dictionaries
    """
    vc_inputs_path = Path(vc_inputs_dir)
    if not vc_inputs_path.exists():
        return []
    
    found_files = []
    
    for filename in filenames:
        # Try to find the file
        matches = list(vc_inputs_path.rglob(filename))
        
        if matches:
            # Use the first match
            audio_file = matches[0]
            
            # Get metadata for this file
            file_metadata = scan_vc_input_files(vc_inputs_dir)
            for metadata in file_metadata:
                if metadata['filename'] == filename:
                    found_files.append(metadata)
                    break
    
    return found_files

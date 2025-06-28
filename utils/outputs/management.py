# utils/outputs/management.py - Generated Content Management Functions

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Tuple

from config import config_manager

logger = logging.getLogger(__name__)


def save_generation_metadata(filename: str, generation_data: Dict[str, Any]) -> bool:
    """
    Save generation metadata as JSON companion file
    
    Args:
        filename: Base filename (without path)
        generation_data: Complete generation context and parameters
    
    Returns:
        True if metadata saved successfully, False otherwise
    """
    try:
        # Get output directory
        output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        
        # Create metadata filename
        base_name = Path(filename).stem
        metadata_file = output_dir / f"{base_name}.json"
        
        # Add timestamp if not present
        if "timestamp" not in generation_data:
            generation_data["timestamp"] = datetime.now().isoformat()
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(generation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved: {metadata_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save metadata for {filename}: {e}")
        return False


def scan_generated_files(outputs_dir: Union[str, Path], generation_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan outputs directory for generated files and their metadata
    
    Args:
        outputs_dir: Path to outputs directory
        generation_type: Filter by generation type ('tts', 'vc', 'concat')
    
    Returns:
        List of file metadata dictionaries
    """
    from ..audio.processing import calculate_audio_duration
    
    outputs_path = Path(outputs_dir)
    if not outputs_path.exists():
        return []
    
    files_metadata = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    for audio_file in outputs_path.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            # Look for companion JSON metadata file
            metadata_file = audio_file.with_suffix(audio_file.suffix + '.json')
            
            # Initialize metadata
            metadata = {
                'filename': audio_file.name,
                'generation_type': 'unknown',
                'created_date': None,
                'file_size_bytes': None,
                'duration_seconds': None,
                'format': audio_file.suffix.lower().lstrip('.'),
                'parameters': {},
                'source_files': [],
                'folder_path': None
            }
            
            # Load from companion JSON if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        json_metadata = json.load(f)
                        metadata.update(json_metadata)
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
                
                # Calculate folder path relative to outputs directory
                relative_path = audio_file.relative_to(outputs_path)
                if relative_path.parent != Path('.'):
                    metadata['folder_path'] = str(relative_path.parent)
                
                # Infer generation type from filename pattern if not set
                if metadata['generation_type'] == 'unknown':
                    filename_lower = audio_file.name.lower()
                    if filename_lower.startswith('tts_'):
                        metadata['generation_type'] = 'tts'
                    elif filename_lower.startswith('vc_'):
                        metadata['generation_type'] = 'vc'
                    elif filename_lower.startswith('concat_'):
                        metadata['generation_type'] = 'concat'
                    else:
                        metadata['generation_type'] = 'unknown'
                
            except Exception as e:
                logger.warning(f"Failed to calculate metadata for {audio_file}: {e}")
            
            # Apply generation type filter
            if generation_type and metadata['generation_type'] != generation_type:
                continue
            
            files_metadata.append(metadata)
    
    # Sort by creation date (newest first)
    files_metadata.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    
    return files_metadata


def find_files_by_names(outputs_dir: Union[str, Path], filenames: List[str]) -> List[Dict[str, Any]]:
    """
    Find specific files by their names in outputs directory
    
    Args:
        outputs_dir: Path to outputs directory
        filenames: List of filenames to find
    
    Returns:
        List of found file metadata dictionaries
    """
    outputs_path = Path(outputs_dir)
    if not outputs_path.exists():
        return []
    
    found_files = []
    
    for filename in filenames:
        # Try to find the file
        matches = list(outputs_path.rglob(filename))
        
        if matches:
            # Use the first match
            audio_file = matches[0]
            
            # Get metadata for this file
            file_metadata = scan_generated_files(outputs_dir)
            for metadata in file_metadata:
                if metadata['filename'] == filename:
                    found_files.append(metadata)
                    break
    
    return found_files


def delete_output_file(output_filename: str) -> Tuple[bool, str, List[str]]:
    """
    Delete an output file and its metadata
    
    Args:
        output_filename: Name of output file to delete (can include path)
    
    Returns:
        (success, message, deleted_files_list)
    """
    outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
    deleted_files = []
    
    # Find the output file
    matches = list(outputs_dir.rglob(output_filename))
    
    if not matches:
        return False, f"Output file not found: {output_filename}", []
    
    output_path = matches[0]  # Use first match
    
    try:
        # Delete the main audio file
        if output_path.exists():
            output_path.unlink()
            deleted_files.append(str(output_path.name))
            logger.info(f"Deleted output file: {output_path}")
        
        # Delete metadata file if it exists
        metadata_path = output_path.with_suffix(output_path.suffix + '.json')
        if metadata_path.exists():
            metadata_path.unlink()
            deleted_files.append(str(metadata_path.name))
            logger.info(f"Deleted output metadata: {metadata_path}")
        
        # Also check for standalone metadata (base_name.json)
        base_metadata_path = output_path.with_suffix('.json')
        if base_metadata_path.exists() and base_metadata_path != metadata_path:
            base_metadata_path.unlink()
            deleted_files.append(str(base_metadata_path.name))
            logger.info(f"Deleted output base metadata: {base_metadata_path}")
        
        return True, f"Output file '{output_filename}' deleted successfully", deleted_files
        
    except Exception as e:
        logger.error(f"Failed to delete output file: {e}")
        return False, f"Failed to delete output file: {e}", deleted_files


def bulk_delete_outputs(folder: Optional[str] = None,
                       generation_type: Optional[str] = None,
                       search: Optional[str] = None,
                       filenames: Optional[List[str]] = None) -> Tuple[bool, str, List[str]]:
    """
    Bulk delete outputs based on criteria
    
    Args:
        folder: Delete outputs in specific folder
        generation_type: Delete outputs of specific type ('tts', 'vc', 'concat')
        search: Delete outputs matching search term
        filenames: Delete specific output filenames
    
    Returns:
        (success, message, deleted_files_list)
    """
    outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
    deleted_files = []
    
    if not outputs_dir.exists():
        return False, "Outputs directory not found", []
    
    # Get all output files matching criteria
    all_files = scan_generated_files(outputs_dir, generation_type=generation_type)
    
    # Filter by folder
    if folder:
        all_files = [f for f in all_files if f.get('folder_path') == folder]
    
    # Filter by search term
    if search:
        search_lower = search.lower()
        all_files = [f for f in all_files if search_lower in f['filename'].lower()]
    
    # Filter by specific filenames
    if filenames:
        all_files = [f for f in all_files if f['filename'] in filenames]
    
    if not all_files:
        return False, "No output files found matching criteria", []
    
    # Delete each file
    total_deleted = 0
    for file_info in all_files:
        success, _, file_deleted_list = delete_output_file(file_info['filename'])
        if success:
            deleted_files.extend(file_deleted_list)
            total_deleted += 1
    
    message = f"Deleted {total_deleted} output file(s)"
    return True, message, deleted_files

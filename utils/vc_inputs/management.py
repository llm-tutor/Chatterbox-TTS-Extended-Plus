# utils/vc_inputs/management.py - VC Input Files Management

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Tuple

from config import config_manager

logger = logging.getLogger(__name__)


def save_uploaded_vc_input(file_content: bytes,
                          filename: str,
                          folder_path: Optional[str] = None,
                          overwrite: bool = False) -> Tuple[bool, str, Optional[Path]]:
    """
    Save uploaded VC input file to vc_inputs directory
    
    Args:
        file_content: File content bytes
        filename: Desired filename
        folder_path: Optional folder organization path
        overwrite: Whether to overwrite existing files
    
    Returns:
        (success, message, saved_path)
    """
    from ..files.naming import sanitize_filename
    
    # Get vc_inputs directory
    vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
    
    # Create target directory path
    if folder_path:
        # Use folder path directly (like TTS does) - don't sanitize to preserve hierarchy
        target_dir = vc_inputs_dir / folder_path
    else:
        target_dir = vc_inputs_dir
    
    # Ensure directory exists
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Failed to create directory: {e}", None
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    target_path = target_dir / safe_filename
    
    # Check if file exists and overwrite policy
    if target_path.exists() and not overwrite:
        return False, f"VC input file already exists: {safe_filename}. Use overwrite=true to replace.", None
    
    # Save file
    try:
        with open(target_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"VC input file saved: {target_path}")
        return True, f"VC input file saved successfully: {safe_filename}", target_path
    except Exception as e:
        logger.error(f"Failed to save VC input file: {e}")
        return False, f"Failed to save VC input file: {e}", None


def create_vc_input_metadata_from_upload(file_path: Path, upload_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create metadata for uploaded VC input file
    
    Args:
        file_path: Path to saved file
        upload_metadata: Metadata from upload request
        
    Returns:
        Complete metadata dictionary
    """
    from ..audio.processing import calculate_audio_duration
    import soundfile as sf
    
    try:
        # Get basic file info
        file_stats = file_path.stat()
        
        # Get audio info
        try:
            with sf.SoundFile(file_path) as audio_file:
                sample_rate = audio_file.samplerate
                duration = len(audio_file) / sample_rate
        except Exception:
            # Fallback to generic duration calculation
            duration = calculate_audio_duration(file_path)
            sample_rate = 22050  # Default fallback
        
        # Calculate folder path
        vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
        relative_path = file_path.relative_to(vc_inputs_dir)
        folder_path = str(relative_path.parent).replace('\\', '/') if relative_path.parent != Path('.') else None
        
        metadata = {
            'filename': file_path.name,
            'folder_path': folder_path,
            'text': upload_metadata.get('text'),
            'file_size_bytes': file_stats.st_size,
            'duration_seconds': duration,
            'sample_rate': sample_rate,
            'format': file_path.suffix.lower().lstrip('.'),
            'created_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'upload_date': datetime.now().isoformat()
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to create VC input metadata: {e}")
        # Return minimal metadata
        return {
            'filename': file_path.name,
            'folder_path': upload_metadata.get('folder_path'),
            'text': upload_metadata.get('text'),
            'file_size_bytes': 0,
            'duration_seconds': 0.0,
            'sample_rate': 22050,
            'format': file_path.suffix.lower().lstrip('.'),
            'created_date': datetime.now().isoformat(),
            'upload_date': datetime.now().isoformat()
        }


def save_vc_input_metadata(file_path: Path, metadata: Dict[str, Any]) -> None:
    """
    Save metadata for VC input file
    
    Args:
        file_path: Path to the audio file
        metadata: Metadata dictionary to save
    """
    metadata_path = file_path.with_suffix(file_path.suffix + '.json')
    
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"VC input metadata saved: {metadata_path}")
    except Exception as e:
        logger.error(f"Failed to save VC input metadata: {e}")


def validate_vc_input_file(file_content: bytes, filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate uploaded VC input file
    
    Args:
        file_content: File content bytes
        filename: Optional filename for validation
        
    Returns:
        (is_valid, error_message)
    """
    # Check file size
    if len(file_content) == 0:
        return False, "File is empty"
    
    # Check file size limit (50MB)
    max_size = 50 * 1024 * 1024
    if len(file_content) > max_size:
        return False, f"File too large. Maximum size is {max_size // (1024*1024)}MB"
    
    # Check file extension if filename provided
    if filename:
        valid_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        file_ext = Path(filename).suffix.lower()
        if file_ext not in valid_extensions:
            return False, f"Unsupported file format. Supported: {', '.join(valid_extensions)}"
    
    return True, "File is valid"


def delete_vc_input_file(vc_input_filename: str) -> Tuple[bool, str, List[str]]:
    """
    Delete a VC input file and its metadata
    
    Args:
        vc_input_filename: Name of VC input file to delete
    
    Returns:
        (success, message, deleted_files_list)
    """
    vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
    deleted_files = []
    
    # Find the VC input file
    matches = list(vc_inputs_dir.rglob(vc_input_filename))
    
    if not matches:
        return False, f"VC input file not found: {vc_input_filename}", []
    
    vc_input_path = matches[0]  # Use first match
    
    try:
        # Delete the main audio file
        if vc_input_path.exists():
            vc_input_path.unlink()
            deleted_files.append(str(vc_input_path.name))
            logger.info(f"Deleted VC input file: {vc_input_path}")
        
        # Delete metadata file if it exists
        metadata_path = vc_input_path.with_suffix(vc_input_path.suffix + '.json')
        if metadata_path.exists():
            metadata_path.unlink()
            deleted_files.append(str(metadata_path.name))
            logger.info(f"Deleted VC input metadata: {metadata_path}")
        
        return True, f"VC input file '{vc_input_filename}' deleted successfully", deleted_files
        
    except Exception as e:
        logger.error(f"Failed to delete VC input file: {e}")
        return False, f"Failed to delete VC input file: {e}", deleted_files


def bulk_delete_vc_inputs(folder: Optional[str] = None,
                         search: Optional[str] = None,
                         filenames: Optional[List[str]] = None) -> Tuple[bool, str, List[str]]:
    """
    Bulk delete VC inputs based on criteria with automatic folder cleanup
    
    Args:
        folder: Delete VC inputs in specific folder
        search: Delete VC inputs matching search term
        filenames: Delete specific VC input filenames
    
    Returns:
        (success, message, deleted_files_list)
    """
    vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
    deleted_files = []
    
    if not vc_inputs_dir.exists():
        return False, "VC inputs directory not found", []
    
    # Get all VC input files matching criteria
    all_files = scan_vc_input_files(vc_inputs_dir, folder=folder)
    
    # Filter by search term (includes filename, folder path, and text content)
    if search:
        search_lower = search.lower()
        all_files = [f for f in all_files if search_lower in f['filename'].lower() or 
                    (f.get('folder_path') and search_lower in f['folder_path'].lower()) or
                    (f.get('text') and search_lower in f['text'].lower())]
    
    # Filter by specific filenames
    if filenames:
        all_files = [f for f in all_files if f['filename'] in filenames]
    
    if not all_files:
        return True, "No VC input files found matching criteria (already clean)", []
    
    # Track which folders had files deleted (for cleanup)
    folders_with_deletions = set()
    
    # Delete each file
    total_deleted = 0
    for file_info in all_files:
        success, _, file_deleted_list = delete_vc_input_file(file_info['filename'])
        if success:
            deleted_files.extend(file_deleted_list)
            total_deleted += 1
            
            # Track the folder for potential cleanup
            if file_info.get('folder_path'):
                folders_with_deletions.add(file_info['folder_path'])
    
    # Clean up empty folders (vc_inputs-specific behavior)
    # Note: This differs from voices where empty subfolders have semantic meaning
    cleaned_folders = []
    for folder_path in folders_with_deletions:
        try:
            target_folder = vc_inputs_dir / folder_path
            # Only remove if folder exists and is empty
            if target_folder.exists() and target_folder.is_dir():
                # Check if folder is empty (no files, no subdirectories)
                if not any(target_folder.iterdir()):
                    target_folder.rmdir()
                    cleaned_folders.append(folder_path)
                    logger.info(f"Cleaned up empty vc_inputs folder: {folder_path}")
        except OSError as e:
            # Log but don't fail the operation if folder cleanup fails
            logger.warning(f"Could not clean up vc_inputs folder {folder_path}: {e}")
    
    # Update message to include folder cleanup info
    message = f"Deleted {total_deleted} VC input file(s)"
    if cleaned_folders:
        message += f" and cleaned up {len(cleaned_folders)} empty folder(s)"
    
    return True, message, deleted_files


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
                    # Use forward slashes for cross-platform consistency
                    metadata['folder_path'] = str(relative_path.parent).replace('\\', '/')
                
            except Exception as e:
                logger.warning(f"Failed to calculate metadata for {audio_file}: {e}")
            
            # Apply folder filter (supports hierarchical deletion)
            if folder:
                folder_path = metadata.get('folder_path')
                # Include files in the exact folder and all subfolders
                if not (folder_path == folder or 
                       (folder_path and folder_path.startswith(folder + '/'))):
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

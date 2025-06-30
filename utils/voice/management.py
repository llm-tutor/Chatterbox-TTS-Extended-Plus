# utils/voice/management.py - Voice File Management Functions

import logging
from pathlib import Path
from typing import Optional, Tuple, List

from config import config_manager
from ..files.naming import sanitize_filename
from .metadata import load_voice_metadata

logger = logging.getLogger(__name__)


def validate_voice_file(file_content: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded voice file for security and format
    
    Args:
        file_content: File content bytes
        filename: Original filename
    
    Returns:
        (is_valid, error_message)
    """
    # File size validation (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    if len(file_content) > max_size:
        return False, f"File too large: {len(file_content)} bytes (max {max_size})"
    
    # File extension validation
    allowed_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    file_ext = Path(filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file format: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
    
    # Basic file signature validation
    audio_signatures = {
        b'RIFF': 'wav',
        b'fLaC': 'flac', 
        b'OggS': 'ogg',
        b'ID3': 'mp3',
        b'\xff\xfb': 'mp3',
        b'\xff\xf3': 'mp3',
        b'\xff\xf2': 'mp3'
    }
    
    # Check file signature
    signature_found = False
    for sig, format_name in audio_signatures.items():
        if file_content.startswith(sig):
            signature_found = True
            break
    
    if not signature_found:
        return False, "File does not appear to be a valid audio file"
    
    return True, ""


def save_uploaded_voice(file_content: bytes, filename: str, folder_path: Optional[str] = None, 
                       overwrite: bool = False) -> Tuple[bool, str, Optional[Path]]:
    """
    Save uploaded voice file to reference_audio directory
    
    Args:
        file_content: File content bytes
        filename: Desired filename
        folder_path: Optional folder organization path
        overwrite: Whether to overwrite existing files
    
    Returns:
        (success, message, saved_path)
    """
    # Get reference audio directory
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    
    # Create target directory path
    if folder_path:
        # Use folder path directly (like TTS does) - don't sanitize to preserve hierarchy
        target_dir = ref_audio_dir / folder_path
    else:
        target_dir = ref_audio_dir
    
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
        return False, f"Voice file already exists: {safe_filename}. Use overwrite=true to replace.", None
    
    # Save file
    try:
        with open(target_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Voice file saved: {target_path}")
        return True, f"Voice file saved successfully: {safe_filename}", target_path
    except Exception as e:
        logger.error(f"Failed to save voice file: {e}")
        return False, f"Failed to save voice file: {e}", None


def delete_voice_file(voice_filename: str) -> Tuple[bool, str, List[str]]:
    """
    Delete a voice file and its metadata
    
    Args:
        voice_filename: Name of voice file to delete
    
    Returns:
        (success, message, deleted_files_list)
    """
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    deleted_files = []
    
    # Find the voice file
    matches = list(ref_audio_dir.rglob(voice_filename))
    
    if not matches:
        return False, f"Voice file not found: {voice_filename}", []
    
    voice_path = matches[0]  # Use first match
    
    try:
        # Delete the audio file
        if voice_path.exists():
            voice_path.unlink()
            deleted_files.append(str(voice_path.name))
            logger.info(f"Deleted voice file: {voice_path}")
        
        # Delete companion metadata file if exists
        metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
        if metadata_path.exists():
            metadata_path.unlink()
            deleted_files.append(str(metadata_path.name))
            logger.info(f"Deleted metadata file: {metadata_path}")
        
        return True, f"Voice '{voice_filename}' deleted successfully", deleted_files
        
    except Exception as e:
        logger.error(f"Failed to delete voice {voice_filename}: {e}")
        return False, f"Failed to delete voice: {e}", deleted_files


def update_voice_metadata_only(voice_filename: str, metadata_updates: dict) -> Tuple[bool, str]:
    """
    Update voice metadata without modifying the audio file
    
    Args:
        voice_filename: Name of voice file
        metadata_updates: Dictionary of metadata fields to update
    
    Returns:
        (success, message)
    """
    from .metadata import save_voice_metadata
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    
    # Find the voice file
    matches = list(ref_audio_dir.rglob(voice_filename))
    
    if not matches:
        return False, f"Voice file not found: {voice_filename}"
    
    voice_path = matches[0]
    
    try:
        # Load existing metadata
        metadata = load_voice_metadata(voice_path)
        
        # Apply updates
        metadata.update(metadata_updates)
        
        # Save updated metadata
        success = save_voice_metadata(voice_path, metadata)
        
        if success:
            return True, f"Metadata updated for voice: {voice_filename}"
        else:
            return False, "Failed to save updated metadata"
    
    except Exception as e:
        logger.error(f"Failed to update metadata for {voice_filename}: {e}")
        return False, f"Failed to update metadata: {e}"

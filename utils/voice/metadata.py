# utils/voice/metadata.py - Voice Metadata Management Functions

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


def load_voice_metadata(voice_file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load voice metadata from companion JSON file or calculate if missing
    
    Args:
        voice_file_path: Path to voice audio file
    
    Returns:
        Dictionary with voice metadata
    """
    from ..audio.processing import calculate_audio_duration
    
    voice_path = Path(voice_file_path)
    metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
    
    # Try to load existing metadata
    metadata = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load metadata for {voice_path}: {e}")
    
    # Calculate missing metadata
    if not metadata.get('name'):
        metadata['name'] = voice_path.stem
    
    if not metadata.get('duration_seconds'):
        metadata['duration_seconds'] = calculate_audio_duration(voice_path)
    
    if not metadata.get('file_size_bytes'):
        try:
            metadata['file_size_bytes'] = voice_path.stat().st_size
        except Exception:
            metadata['file_size_bytes'] = None
    
    if not metadata.get('format'):
        metadata['format'] = voice_path.suffix.lower().lstrip('.')
    
    if not metadata.get('sample_rate'):
        try:
            import soundfile as sf
            with sf.SoundFile(str(voice_path)) as f:
                metadata['sample_rate'] = f.samplerate
        except Exception:
            metadata['sample_rate'] = None
    
    if not metadata.get('created_date'):
        try:
            created_time = voice_path.stat().st_ctime
            metadata['created_date'] = datetime.fromtimestamp(created_time).isoformat()
        except Exception:
            metadata['created_date'] = None
    
    # Ensure required fields have defaults
    metadata.setdefault('description', f"Voice file: {voice_path.name}")
    metadata.setdefault('tags', [])
    metadata.setdefault('usage_count', 0)
    metadata.setdefault('default_parameters', {})
    
    # Calculate relative URL path for TTS generation
    from config import config_manager
    reference_audio_dir = Path(config_manager.get("paths.reference_audio_dir"))
    try:
        # Get relative path from reference_audio dir using forward slashes
        relative_path = voice_path.relative_to(reference_audio_dir)
        metadata['url'] = str(relative_path).replace('\\', '/')
    except ValueError:
        # File is not in reference_audio dir, use filename only
        metadata['url'] = voice_path.name
    
    return metadata


def save_voice_metadata(voice_file_path: Union[str, Path], metadata: Dict[str, Any]) -> bool:
    """
    Save voice metadata to companion JSON file
    
    Args:
        voice_file_path: Path to voice audio file
        metadata: Metadata dictionary to save
    
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        voice_path = Path(voice_file_path)
        metadata_path = voice_path.with_suffix(voice_path.suffix + '.json')
        
        # Update timestamp
        metadata['last_updated'] = datetime.now().isoformat()
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Voice metadata saved: {metadata_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save voice metadata for {voice_file_path}: {e}")
        return False


def update_voice_usage(voice_file_path: Union[str, Path]) -> None:
    """
    Update voice usage statistics
    
    Args:
        voice_file_path: Path to voice audio file
    """
    try:
        metadata = load_voice_metadata(voice_file_path)
        metadata['usage_count'] = metadata.get('usage_count', 0) + 1
        metadata['last_used'] = datetime.now().isoformat()
        save_voice_metadata(voice_file_path, metadata)
    except Exception as e:
        logger.warning(f"Failed to update voice usage for {voice_file_path}: {e}")


def create_voice_metadata_from_upload(voice_path: Path, upload_metadata: dict) -> dict:
    """
    Create comprehensive voice metadata from uploaded file and user input
    
    Args:
        voice_path: Path to saved voice file
        upload_metadata: Metadata from upload request
    
    Returns:
        Complete metadata dictionary
    """
    # Start with calculated metadata
    metadata = load_voice_metadata(voice_path)
    
    # Override with user-provided metadata
    if upload_metadata.get('name'):
        metadata['name'] = upload_metadata['name']
    
    if upload_metadata.get('description'):
        metadata['description'] = upload_metadata['description']
    
    if upload_metadata.get('tags'):
        metadata['tags'] = upload_metadata['tags']
    
    if upload_metadata.get('default_parameters'):
        metadata['default_parameters'] = upload_metadata['default_parameters']
    
    # Set upload timestamp
    metadata['uploaded_date'] = datetime.now().isoformat()
    
    return metadata

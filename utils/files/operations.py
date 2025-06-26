# utils/files/operations.py - File Operations Functions

import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def validate_audio_file(file_path: Path) -> bool:
    """Validate if file is a supported audio format"""
    if not file_path.exists():
        return False
    
    supported_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    return file_path.suffix.lower() in supported_extensions


def get_file_size(file_path: Path) -> Optional[int]:
    """Get file size in bytes"""
    try:
        return file_path.stat().st_size
    except Exception:
        return None


def ensure_directory_exists(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)


def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> None:
    """Clean up old files in directory"""
    if not directory.exists():
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    logger.debug(f"Cleaned up old file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {e}")

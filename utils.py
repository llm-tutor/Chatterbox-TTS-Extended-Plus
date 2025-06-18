# utils.py - Utility functions for Chatterbox TTS Extended Plus

import os
import logging
import hashlib
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import torch
import random
import numpy as np

logger = logging.getLogger(__name__)


def generate_unique_filename(prefix: str = "output", extension: str = "wav") -> str:
    """Generate a unique filename with timestamp and hash"""
    timestamp = int(time.time())
    random_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_hash}.{extension}"


def validate_audio_file(file_path: Path) -> bool:
    """Validate if file is a supported audio format"""
    if not file_path.exists():
        return False
    
    supported_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    return file_path.suffix.lower() in supported_extensions


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    # Remove/replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    return filename


def get_audio_duration(file_path: Path) -> Optional[float]:
    """Get audio file duration in seconds"""
    try:
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            return len(f) / f.samplerate
    except Exception as e:
        logger.warning(f"Could not get duration for {file_path}: {e}")
        return None


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


def is_url(text: str) -> bool:
    """Check if text is a valid URL"""
    return text.startswith(('http://', 'https://'))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_text_length(text: str, max_length: int = 10000) -> bool:
    """Validate text length for TTS generation"""
    return len(text.strip()) > 0 and len(text) <= max_length


def normalize_audio_path(path_input: Union[str, Path]) -> Path:
    """Normalize audio path input to Path object"""
    if isinstance(path_input, str):
        return Path(path_input)
    return path_input


def get_supported_audio_formats() -> List[str]:
    """Get list of supported audio formats"""
    return ["wav", "mp3", "flac"]


def validate_audio_format(format_name: str) -> bool:
    """Validate if audio format is supported"""
    return format_name.lower() in get_supported_audio_formats()


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted and safe"""
    import re
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Check for potentially dangerous URLs (localhost and private IPs)
    dangerous_patterns = [
        r'.*localhost.*',
        r'.*127\.0\.0\.1.*',
        r'.*0\.0\.0\.0.*',
        r'.*192\.168\..*',
        r'.*10\..*',
        r'.*172\.(1[6-9]|2[0-9]|3[0-1])\..*',  # Private IP ranges
    ]
    
    for pattern in dangerous_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return False
    
    return True


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path for safe usage"""
    import os
    
    # Convert to Path and resolve any relative components
    path = Path(file_path)
    
    # Remove any directory traversal attempts
    path_parts = []
    for part in path.parts:
        if part in ('..', '.'):
            continue
        part = sanitize_filename(part)
        path_parts.append(part)
    
    # Reconstruct path using forward slashes (cross-platform)
    if path_parts:
        return '/'.join(path_parts)
    else:
        return "unnamed"


def validate_text_input(text: str) -> tuple[bool, str]:
    """
    Validate and sanitize text input for TTS generation
    Returns (is_valid, sanitized_text)
    """
    if not text or not text.strip():
        return False, ""
    
    text = text.strip()
    
    # Check length
    max_length = 10000  # Could be configurable
    if len(text) > max_length:
        return False, text[:max_length]
    
    # Basic sanitization - remove potential control characters
    import re
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return True, text

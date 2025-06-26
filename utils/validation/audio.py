# utils/validation/audio.py - Audio Validation Functions

from typing import List


def get_supported_audio_formats() -> List[str]:
    """Get list of supported audio formats"""
    return ["wav", "mp3", "flac"]


def validate_audio_format(format_name: str) -> bool:
    """Validate if audio format is supported"""
    return format_name.lower() in get_supported_audio_formats()

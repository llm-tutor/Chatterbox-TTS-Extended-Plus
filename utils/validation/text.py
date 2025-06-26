# utils/validation/text.py - Text Validation Functions

from typing import Tuple


def validate_text_length(text: str, max_length: int = 2000) -> bool:
    """Validate text length for TTS generation"""
    return len(text.strip()) > 0 and len(text) <= max_length


def validate_text_input(text: str) -> Tuple[bool, str]:
    """
    Validate and sanitize text input for TTS generation
    Returns (is_valid, sanitized_text)
    """
    if not text or not isinstance(text, str):
        return False, ""
    
    # Basic sanitization
    sanitized = text.strip()
    
    # Check if empty after stripping
    if not sanitized:
        return False, ""
    
    # Basic length check (reasonable limit for TTS)
    if len(sanitized) > 10000:  # 10k character limit
        return False, "Text too long"
    
    return True, sanitized

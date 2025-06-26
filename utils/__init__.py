# utils/__init__.py - Modular Utils Package
"""
Chatterbox TTS Extended Plus - Utilities Package

This package provides modular utility functions organized by functionality:

- audio: Audio processing, trimming, and analysis
- concatenation: Audio concatenation and mixing
- files: File operations, naming, and validation  
- formatting: Display formatting utilities
- outputs: Generated content management
- validation: Input validation and sanitization
- voice: Voice metadata and management

Usage:
    from utils.audio.processing import apply_speed_factor
    from utils.voice.metadata import load_voice_metadata
    from utils.files.naming import generate_enhanced_filename
"""

__version__ = "2.0.0"
__author__ = "Chatterbox TTS Extended Plus"

# Module documentation
__all__ = [
    "audio", "concatenation", "files", "formatting", 
    "outputs", "validation", "voice"
]

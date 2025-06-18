# exceptions.py - Custom exception hierarchy for Chatterbox TTS Extended Plus

class ChatterboxAPIError(Exception):
    """Base exception for all API errors"""
    pass


class ModelLoadError(ChatterboxAPIError):
    """Raised when model loading fails"""
    pass


class GenerationError(ChatterboxAPIError):
    """Raised when TTS/VC generation fails"""
    pass


class AudioProcessingError(ChatterboxAPIError):
    """Raised when audio processing fails"""
    pass


class ValidationError(ChatterboxAPIError):
    """Raised when input validation fails"""
    pass


class ResourceError(ChatterboxAPIError):
    """Raised when resource access fails (files, URLs)"""
    pass


class ConfigurationError(ChatterboxAPIError):
    """Raised when configuration is invalid"""
    pass


class NetworkError(ChatterboxAPIError):
    """Raised when network operations fail (downloads, etc.)"""
    pass


class FileSystemError(ChatterboxAPIError):
    """Raised when file system operations fail"""
    pass

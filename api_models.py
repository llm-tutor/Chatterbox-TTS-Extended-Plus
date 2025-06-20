# api_models.py - Pydantic models for API requests and responses

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from utils import validate_text_length, validate_audio_format, validate_text_input


# Base models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: str
    timestamp: Optional[str] = None


# TTS Models
class TTSRequest(BaseModel):
    """Request model for TTS generation"""
    text: str = Field(..., description="Text to generate speech from")
    reference_audio_filename: Optional[str] = Field(None, description="Reference audio filename")
    exaggeration: float = Field(0.5, ge=0.0, le=2.0, description="Speech exaggeration level")
    temperature: float = Field(0.75, ge=0.1, le=2.0, description="Generation temperature")
    seed: int = Field(0, ge=0, description="Random seed (0 for random)")
    cfg_weight: float = Field(1.0, ge=0.0, le=2.0, description="CFG weight")
    num_candidates_per_chunk: int = Field(3, ge=1, le=10, description="Candidates per chunk")
    max_attempts_per_candidate: int = Field(3, ge=1, le=10, description="Max attempts per candidate")
    bypass_whisper_checking: bool = Field(False, description="Bypass Whisper validation")
    whisper_model_name: str = Field("medium", description="Whisper model size")
    use_faster_whisper: bool = Field(True, description="Use faster-whisper implementation")
    use_longest_transcript_on_fail: bool = Field(True, description="Use longest transcript on failure")
    enable_batching: bool = Field(False, description="Enable text batching")
    smart_batch_short_sentences: bool = Field(True, description="Smart batching for short sentences")
    to_lowercase: bool = Field(True, description="Convert text to lowercase")
    normalize_spacing: bool = Field(True, description="Normalize text spacing")
    fix_dot_letters: bool = Field(True, description="Fix dot letters in text")
    remove_reference_numbers: bool = Field(True, description="Remove reference numbers")
    use_auto_editor: bool = Field(False, description="Use auto editor for audio")
    keep_original_wav_ae: bool = Field(False, description="Keep original WAV with auto editor")
    ae_threshold: float = Field(0.06, ge=0.0, le=1.0, description="Auto editor threshold")
    ae_margin: float = Field(0.2, ge=0.0, le=1.0, description="Auto editor margin")
    normalize_audio: bool = Field(False, description="Normalize output audio")
    normalize_method: str = Field("ebu", description="Audio normalization method")
    normalize_level: float = Field(-24.0, description="Normalization level")
    normalize_tp: float = Field(-2.0, description="True peak level")
    normalize_lra: float = Field(7.0, description="Loudness range")
    sound_words_field: str = Field("", description="Sound words field")
    export_formats: List[str] = Field(["wav", "mp3"], description="Export formats")
    disable_watermark: bool = Field(True, description="Disable watermark")

    @validator('text')
    def validate_text_content(cls, v):
        is_valid, sanitized_text = validate_text_input(v)
        if not is_valid:
            raise ValueError("Text must be non-empty and under length limit")
        return sanitized_text

    @validator('export_formats')
    def validate_formats(cls, v):
        for fmt in v:
            if not validate_audio_format(fmt):
                raise ValueError(f"Unsupported audio format: {fmt}")
        return v

    @validator('whisper_model_name')
    def validate_whisper_model(cls, v):
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if v not in valid_models:
            raise ValueError(f"Invalid Whisper model: {v}")
        return v

    @validator('reference_audio_filename')
    def validate_reference_audio(cls, v):
        from utils import sanitize_file_path
        if v is not None:
            v = v.strip()
            # If it's not a URL, sanitize the file path
            if not v.startswith(('http://', 'https://')):
                v = sanitize_file_path(v)
        return v


# VC Models
class VCRequest(BaseModel):
    """Request model for Voice Conversion"""
    input_audio_source: str = Field(..., description="Input audio source (filename or URL)")
    target_voice_source: str = Field(..., description="Target voice source (filename or URL)")
    chunk_sec: int = Field(60, ge=1, le=300, description="Chunk size in seconds")
    overlap_sec: float = Field(0.1, ge=0.0, le=5.0, description="Overlap in seconds")
    disable_watermark: bool = Field(True, description="Disable watermark")
    export_formats: List[str] = Field(["wav", "mp3"], description="Export formats")

    @validator('input_audio_source', 'target_voice_source')
    def validate_audio_sources(cls, v):
        from utils import sanitize_file_path
        if not v or not v.strip():
            raise ValueError("Audio source cannot be empty")
        
        v = v.strip()
        
        # If it's not a URL, sanitize the file path
        if not v.startswith(('http://', 'https://')):
            v = sanitize_file_path(v)
        
        return v

    @validator('export_formats')
    def validate_formats(cls, v):
        for fmt in v:
            if not validate_audio_format(fmt):
                raise ValueError(f"Unsupported audio format: {fmt}")
        return v


# Response Models
class AudioFile(BaseModel):
    """Audio file information"""
    format: str
    filename: str
    url: str
    path: Optional[str] = None


class TTSResponse(BaseResponse):
    """Response model for TTS generation"""
    output_files: List[AudioFile] = []
    generation_seed_used: Optional[int] = None
    processing_time_seconds: Optional[float] = None


class VCResponse(BaseResponse):
    """Response model for Voice Conversion"""
    output_files: List[AudioFile] = []
    processing_time_seconds: Optional[float] = None


# Utility endpoint models
class HealthResponse(BaseModel):
    """Enhanced health check response with metrics"""
    status: str
    models_loaded: Dict[str, bool]
    version: str
    uptime_seconds: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    resource_status: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None


class ConfigResponse(BaseModel):
    """Configuration information response"""
    tts_defaults: Dict[str, Any]
    vc_defaults: Dict[str, Any]
    supported_formats: List[str]
    api_limits: Dict[str, Any]


class VoiceInfo(BaseModel):
    """Voice information"""
    path: str
    name: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None


class VoicesResponse(BaseModel):
    """Available voices response"""
    voices: List[VoiceInfo]
    count: int

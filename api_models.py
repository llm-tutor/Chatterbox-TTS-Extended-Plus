# api_models.py - Pydantic models for API requests and responses

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, model_validator, field_validator
from utils import validate_text_length, validate_audio_format, validate_text_input
from config import config_manager

def get_default_speed_factor() -> float:
    """Get the configured default speed factor"""
    return config_manager.get("speed_factor.default_speed_factor", 1.0)


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
    speed_factor: float = Field(1.0, ge=0.5, le=2.0, description="Speed adjustment factor (0.5x to 2.0x)")
    speed_factor_library: Optional[str] = Field(
        "auto", 
        description="Library for speed adjustment: 'auto', 'audiostretchy', 'librosa', 'torchaudio'. 'auto' selects audiostretchy for speech quality, with clean fallback chain."
    )
    trim: bool = Field(False, description="Apply silence trimming to generated audio")
    trim_threshold_ms: int = Field(200, ge=50, le=1000, description="Silence threshold for trimming in milliseconds")
    export_formats: List[str] = Field(["wav", "mp3"], description="Export formats")
    disable_watermark: bool = Field(True, description="Disable watermark")

    @model_validator(mode='before')
    @classmethod
    def apply_config_defaults(cls, values):
        """Apply configuration-based defaults"""
        # Apply configured default speed factor if not explicitly set
        if isinstance(values, dict):
            if 'speed_factor' not in values or values.get('speed_factor') == 1.0:
                config_default = get_default_speed_factor()
                if config_default != 1.0:
                    values['speed_factor'] = config_default
        
        return values

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

    @validator('speed_factor_library')
    def validate_speed_factor_library(cls, v):
        if v is not None:
            allowed_libraries = ['auto', 'audiostretchy', 'librosa', 'torchaudio']
            if v not in allowed_libraries:
                raise ValueError(f"speed_factor_library must be one of: {allowed_libraries}")
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
    error_summary: Optional[Dict[str, Any]] = None  # NEW: Error tracking summary


class ErrorSummaryResponse(BaseModel):
    """Error summary response for error tracking endpoint"""
    total_errors: int
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    by_operation: Dict[str, int]
    most_frequent: Dict[str, int]
    unresolved_count: int
    recent_errors: List[Dict[str, Any]]


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


class VoiceMetadata(BaseModel):
    """Enhanced voice metadata"""
    name: str
    description: Optional[str] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    file_size_bytes: Optional[int] = None
    format: Optional[str] = None
    default_parameters: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    created_date: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0
    folder_path: Optional[str] = None


class VoicesResponse(BaseModel):
    """Enhanced available voices response with pagination"""
    voices: List[VoiceMetadata]
    count: int
    page: int = 1
    page_size: int = 50
    total_pages: int = 1
    has_next: bool = False
    has_previous: bool = False


# Voice Upload Models
class VoiceUploadRequest(BaseModel):
    """Request model for voice upload (metadata part)"""
    name: Optional[str] = Field(None, description="Voice name (defaults to filename)")
    description: Optional[str] = Field(None, description="Voice description")
    tags: Optional[List[str]] = Field(default_factory=list, description="Voice tags")
    folder_path: Optional[str] = Field(None, description="Folder organization path")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default TTS parameters")
    overwrite: bool = Field(False, description="Overwrite existing voice file")


class VoiceUploadResponse(BaseModel):
    """Response model for voice upload"""
    success: bool = True
    message: str = "Voice uploaded successfully"
    voice_metadata: VoiceMetadata
    filename: str


class VoiceMetadataUpdateRequest(BaseModel):
    """Request model for voice metadata updates"""
    name: Optional[str] = Field(None, description="Voice name")
    description: Optional[str] = Field(None, description="Voice description")
    tags: Optional[List[str]] = Field(None, description="Voice tags")
    folder_path: Optional[str] = Field(None, description="Folder organization path")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default TTS parameters")


class VoiceDeletionResponse(BaseModel):
    """Response model for voice deletion"""
    success: bool = True
    message: str = "Voice deleted successfully"
    deleted_files: List[str] = Field(default_factory=list, description="List of deleted files")
    deleted_count: int = 0


class VoiceFolderInfo(BaseModel):
    """Information about a voice folder"""
    path: str
    voice_count: int
    subfolders: List[str] = Field(default_factory=list)


class VoiceFoldersResponse(BaseModel):
    """Response for voice folders structure"""
    folders: List[VoiceFolderInfo]
    total_folders: int
    total_voices: int


# Generated Files Models
class GeneratedFileMetadata(BaseModel):
    """Metadata for generated audio files"""
    filename: str
    generation_type: str  # 'tts', 'vc', 'concat'
    created_date: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    format: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    source_files: Optional[List[str]] = None  # For VC and concat operations
    folder_path: Optional[str] = None


class GeneratedFilesResponse(BaseModel):
    """Response for generated files listing"""
    files: List[GeneratedFileMetadata]
    count: int
    page: int = 1
    page_size: int = 50
    total_pages: int = 1
    has_next: bool = False
    has_previous: bool = False
    total_files: int = 0


# Audio Concatenation Models
class ConcatRequest(BaseModel):
    """Request model for audio concatenation"""
    files: List[str] = Field(
        ..., 
        min_length=1, 
        description="List of filenames and silence notations. Use '(duration[ms|s])' for silence: ['file1.wav', '(500ms)', 'file2.wav']",
        examples=[
            ["intro.wav", "main.wav", "outro.wav"],
            ["(1s)", "speech.wav", "(500ms)", "music.wav", "(2s)"]
        ]
    )
    export_formats: List[str] = Field(default=["wav"], description="Output formats")
    normalize_levels: bool = Field(default=True, description="Normalize audio levels")
    crossfade_ms: int = Field(default=0, ge=0, le=5000, description="Crossfade duration in milliseconds")
    pause_duration_ms: int = Field(default=0, ge=0, le=3000, description="Base pause duration between clips in milliseconds (0 = no pause, ignored when using manual silence)")
    pause_variation_ms: int = Field(default=200, ge=0, le=500, description="Random variation in pause duration (+/-) in milliseconds (ignored when using manual silence)")
    trim: bool = Field(default=False, description="Remove extraneous silence from input files before concatenation")
    trim_threshold_ms: int = Field(default=200, ge=50, le=1000, description="Minimum silence duration (ms) to consider for trimming")
    output_filename: Optional[str] = Field(None, description="Custom output filename (without extension)")
    response_mode: str = Field(default="stream", description="Response mode: 'stream' or 'url'")

    @field_validator('export_formats')
    @classmethod
    def validate_export_formats(cls, v):
        valid_formats = {'wav', 'mp3', 'flac'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}. Must be one of {valid_formats}")
        return v

    @field_validator('files')
    @classmethod
    def validate_files_list(cls, v):
        import re
        
        if not v:
            raise ValueError("Files array cannot be empty")
        
        # Validate silence notation and count actual audio files
        silence_pattern = re.compile(r'^\((\d+(?:\.\d+)?)(ms|s)\)$')
        audio_file_count = 0
        
        for item in v:
            if silence_pattern.match(item):
                # Validate silence duration
                match = silence_pattern.match(item)
                duration_value = float(match.group(1))
                unit = match.group(2)
                duration_ms = duration_value * 1000 if unit == 's' else duration_value
                
                if not (50 <= duration_ms <= 10000):
                    raise ValueError(f"Silence duration must be between 50ms and 10s: {item}")
            else:
                # Count as audio file
                audio_file_count += 1
        
        # Need at least one audio file
        if audio_file_count == 0:
            raise ValueError("At least one audio file required (silence-only concatenation not allowed)")
        
        # If no silence notation is used, require at least 2 files (original behavior)
        has_silence = any(silence_pattern.match(item) for item in v)
        if not has_silence and audio_file_count < 2:
            raise ValueError("At least 2 files required for concatenation when not using manual silence")
        
        return v

    @field_validator('pause_variation_ms')
    @classmethod
    def validate_pause_variation(cls, v, info):
        if 'pause_duration_ms' in info.data:
            base_duration = info.data['pause_duration_ms']
            if base_duration > 0 and v >= base_duration:
                raise ValueError("Pause variation must be less than base pause duration when pause is enabled")
        return v


class ConcatResponse(BaseModel):
    """Response model for audio concatenation"""
    success: bool = True
    message: str = "Audio concatenation completed successfully"
    output_files: List[str] = Field(default_factory=list, description="Generated concatenated files")
    total_duration_seconds: Optional[float] = None
    file_count: int = 0
    processing_time_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

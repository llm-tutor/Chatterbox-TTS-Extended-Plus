# Request Models

> **Chatterbox TTS Extended Plus** - Complete API request schemas and validation rules

## Overview

This document describes all request models used by the Chatterbox TTS API, including validation rules, default values, and usage examples.

## Base Request Structure

All API requests use JSON format with the following content type:
```
Content-Type: application/json
```

For file upload requests, use multipart form data:
```
Content-Type: multipart/form-data
```

## TTS Request Model

### TTSRequest Schema

```json
{
  "text": "string (required)",
  "reference_audio_filename": "string (optional)",
  "exaggeration": 0.5,
  "temperature": 0.75,
  "seed": 0,
  "cfg_weight": 1.0,
  "num_candidates_per_chunk": 3,
  "max_attempts_per_candidate": 3,
  "bypass_whisper_checking": false,
  "whisper_model_name": "medium",
  "use_faster_whisper": true,
  "use_longest_transcript_on_fail": true,
  "enable_batching": false,
  "smart_batch_short_sentences": true,
  "to_lowercase": true,
  "normalize_spacing": true,
  "fix_dot_letters": true,
  "remove_reference_numbers": true,
  "use_auto_editor": false,
  "keep_original_wav_ae": false,
  "ae_threshold": 0.06,
  "ae_margin": 0.2,
  "normalize_audio": false,
  "normalize_method": "ebu",
  "normalize_level": -24.0,
  "normalize_tp": -2.0,
  "normalize_lra": 7.0,
  "sound_words_field": "",
  "speed_factor": 1.0,
  "speed_factor_library": "auto",
  "export_formats": ["wav", "mp3"],
  "disable_watermark": true
}
```

### Field Descriptions

#### Core Parameters

| Field | Type | Required | Range | Default | Description |
|-------|------|----------|-------|---------|-------------|
| `text` | string | **Yes** | 1-10000 chars | - | Text to generate speech from |
| `reference_audio_filename` | string | No | - | null | Reference voice file (in reference_audio/) |
| `speed_factor` | number | No | 0.5-2.0 | 1.0 | Speed adjustment factor |
| `export_formats` | array | No | - | ["wav", "mp3"] | Output audio formats |

#### Generation Parameters

| Field | Type | Range | Default | Description |
|-------|------|-------|---------|-------------|
| `exaggeration` | number | 0.0-2.0 | 0.5 | Speech exaggeration level |
| `temperature` | number | 0.1-2.0 | 0.75 | Generation randomness |
| `seed` | integer | 0+ | 0 | Random seed (0 = random) |
| `cfg_weight` | number | 0.0-2.0 | 1.0 | Classifier-free guidance weight |

#### Audio Processing

| Field | Type | Range | Default | Description |
|-------|------|-------|---------|-------------|
| `num_candidates_per_chunk` | integer | 1-10 | 3 | Generation candidates per chunk |
| `max_attempts_per_candidate` | integer | 1-10 | 3 | Max retry attempts per candidate |
| `bypass_whisper_checking` | boolean | - | false | Skip Whisper validation |
| `whisper_model_name` | string | See below | "medium" | Whisper model size |

**Valid Whisper Models**: `"tiny"`, `"base"`, `"small"`, `"medium"`, `"large"`

#### Text Processing

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_batching` | boolean | false | Enable text batching |
| `smart_batch_short_sentences` | boolean | true | Smart batching for short sentences |
| `to_lowercase` | boolean | true | Convert text to lowercase |
| `normalize_spacing` | boolean | true | Normalize text spacing |
| `fix_dot_letters` | boolean | true | Fix dot letters in text |
| `remove_reference_numbers` | boolean | true | Remove reference numbers |

### Speed Factor Configuration

| Field | Type | Range | Default | Description |
|-------|------|-------|---------|-------------|
| `speed_factor` | number | 0.5-2.0 | 1.0 | Playback speed multiplier |
| `speed_factor_library` | string | See below | "auto" | Speed processing library |

**Valid Speed Libraries**: `"auto"`, `"audiostretchy"`, `"librosa"`, `"torchaudio"`

**Speed Factor Examples**:
- `0.5` = Half speed (slower)
- `1.0` = Normal speed
- `1.5` = 1.5x speed (faster)
- `2.0` = Double speed (maximum)

### Audio Export Formats

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `export_formats` | array | ["wav", "mp3"] | Output formats |

**Supported Formats**: `"wav"`, `"mp3"`, `"flac"`

### Validation Rules

#### Text Validation
```python
# Text requirements
- Non-empty string
- Maximum 10,000 characters
- Automatically sanitized (whitespace trimmed)
```

#### Reference Audio Validation
```python
# File path requirements
- Must exist in reference_audio/ directory
- Supports subdirectories
- File extensions: .wav, .mp3, .flac
- URLs are supported (http:// or https://)
```

### Example Requests

#### Minimal Request
```json
{
  "text": "Hello world"
}
```

#### Complete Request
```json
{
  "text": "Welcome to our presentation",
  "reference_audio_filename": "professional_speaker.wav",
  "temperature": 0.8,
  "speed_factor": 1.1,
  "export_formats": ["wav", "mp3"],
  "normalize_audio": true,
  "normalize_level": -23.0
}
```

#### Custom Voice with URL
```json
{
  "text": "Download and use this voice",
  "reference_audio_filename": "https://example.com/voice.wav",
  "temperature": 0.9,
  "seed": 42
}
```
## Voice Conversion Request Model

### VCRequest Schema

```json
{
  "input_audio_source": "string (required)",
  "target_voice_source": "string (required)",
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "disable_watermark": true,
  "export_formats": ["wav", "mp3"]
}
```

### Field Descriptions

| Field | Type | Required | Range | Default | Description |
|-------|------|----------|-------|---------|-------------|
| `input_audio_source` | string | **Yes** | - | - | Input audio file or URL |
| `target_voice_source` | string | **Yes** | - | - | Target voice file |
| `chunk_sec` | integer | No | 1-300 | 60 | Processing chunk size in seconds |
| `overlap_sec` | number | No | 0.0-5.0 | 0.1 | Overlap between chunks |
| `disable_watermark` | boolean | No | - | true | Disable audio watermark |
| `export_formats` | array | No | - | ["wav", "mp3"] | Output formats |

### File Resolution

#### Input Audio Source
- **Server Files**: Must be in `vc_inputs/` directory
- **URLs**: Downloaded automatically to temp directory
- **Upload**: Use multipart/form-data (see file upload guide)

#### Target Voice Source  
- **Server Files**: Must be in `reference_audio/` directory
- **URLs**: Downloaded automatically to temp directory

### Example Requests

#### Server Files
```json
{
  "input_audio_source": "meeting_recording.wav",
  "target_voice_source": "professional_speaker.wav",
  "chunk_sec": 30,
  "export_formats": ["wav"]
}
```

#### URL Input with Server Target
```json
{
  "input_audio_source": "https://example.com/podcast.mp3",
  "target_voice_source": "narrator.wav",
  "chunk_sec": 90,
  "overlap_sec": 0.2
}
```
## Voice Management Request Models

### VoiceUploadRequest Schema

```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "tags": ["string", "..."] (optional),
  "folder_path": "string (optional)", 
  "default_parameters": {} (optional),
  "overwrite": false
}
```

### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | No | filename | Display name for voice |
| `description` | string | No | null | Voice description |
| `tags` | array | No | [] | Categorization tags |
| `folder_path` | string | No | null | Organization path |
| `default_parameters` | object | No | null | Default TTS parameters |
| `overwrite` | boolean | No | false | Overwrite existing file |

### Example Voice Upload

**Multipart Request**:
```bash
curl -X POST http://localhost:7860/api/v1/voice \
  -F "audio_file=@speaker.wav" \
  -F "name=Professional Speaker" \
  -F "description=Clear, authoritative business voice" \
  -F "tags=[\"business\", \"professional\", \"clear\"]" \
  -F "folder_path=corporate/executives"
```

### VoiceMetadataUpdateRequest Schema

```json
{
  "name": "string (optional)",
  "description": "string (optional)", 
  "tags": ["string", "..."] (optional),
  "folder_path": "string (optional)",
  "default_parameters": {} (optional)
}
```

**Usage**: Update existing voice metadata without changing audio file.

## Query Parameters

### Pagination Parameters

Available on list endpoints (`/voices`, `/outputs`):

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `page` | integer | 1+ | 1 | Page number |
| `page_size` | integer | 1-100 | 50 | Items per page |

### Search and Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search voice names and descriptions |
| `generation_type` | string | Filter by: "tts", "vc", "concat" |
| `filenames` | string | Comma-separated filenames to lookup |

### Response Mode Parameter

Available on generation endpoints (`/tts`, `/vc`):

| Parameter | Type | Values | Default | Description |
|-----------|------|--------|---------|-------------|
| `response_mode` | string | "stream", "url" | "stream" | Response format |

## Validation Rules Summary

### Text Validation
- Non-empty string
- Maximum 10,000 characters
- Automatically sanitized (whitespace trimmed)

### Audio File Validation
- File paths are sanitized
- URLs must start with http:// or https://
- Server files checked for existence in appropriate directories

### Format Validation
- Export formats must be: "wav", "mp3", or "flac"
- Whisper models must be: "tiny", "base", "small", "medium", "large"
- Speed factor libraries must be: "auto", "audiostretchy", "librosa", "torchaudio"

## See Also

- [Response Models](response-models.md) - API response schemas
- [Examples Collection](examples/) - Complete request/response examples
- [Streaming Responses Guide](../guides/streaming-responses.md) - Response handling
- [File Uploads Guide](../guides/file-uploads.md) - Upload request formats
- [Error Handling Guide](../guides/error-handling.md) - Validation error handling

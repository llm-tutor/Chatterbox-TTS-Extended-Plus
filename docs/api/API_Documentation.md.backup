# Chatterbox TTS Extended Plus - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:7860`  
**API Prefix:** `/api/v1`

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [File Access](#file-access)
7. [Advanced Features](#advanced-features)
8. [Configuration](#configuration)
9. [Examples](#examples)

## Quick Start

### 1. Start the Server
```bash
python main_api.py
```
The server will start on `http://localhost:7860`

### 2. Test the API
```bash
# Health check
curl http://localhost:7860/api/v1/health

# Simple TTS generation
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test of the TTS API."}'
```

### 3. Access Generated Files
Generated audio files are accessible via HTTP at: `http://localhost:7860/outputs/{filename}`

## Authentication

**No authentication required** - This API is designed for local/personal use.

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check and system status |
| `/api/v1/tts` | POST | Text-to-Speech generation |
| `/api/v1/vc` | POST | Voice conversion |
| `/api/v1/config` | GET | Configuration information |
| `/api/v1/voices` | GET | Available reference voices (with pagination) |

### Voice Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/voice` | POST | Upload voice file with metadata |
| `/api/v1/voice/{filename}` | DELETE | Delete single voice file |
| `/api/v1/voice/{filename}/metadata` | PUT | Update voice metadata only |
| `/api/v1/voices` | DELETE | Bulk delete voices by criteria |
| `/api/v1/voices/folders` | GET | Get voice folder structure |

### Generated Files

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/outputs` | GET | List generated files with metadata |

### Static File Serving

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/outputs/{filename}` | GET | Download generated audio files |
| `/ui` | GET | Gradio web interface (optional) |

## Request/Response Formats

### Common Response Structure

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2025-06-18T20:30:00Z"
}
```

### Error Response Structure

```json
{
  "success": false,
  "error": "Descriptive error message",
  "detail": "Technical details for debugging",
  "error_code": "ERROR_TYPE",
  "timestamp": "2025-06-18T20:30:00Z"
}
```

### Audio File Object

```json
{
  "format": "wav",
  "filename": "output_12345.wav",
  "url": "/outputs/output_12345.wav",
  "path": "/full/path/to/file"
}
```

## API Endpoints Detail

### 1. Health Check

**GET** `/api/v1/health`

Check API health and system status.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "tts": true,
    "vc": true,
    "whisper": true
  },
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

### 2. Text-to-Speech Generation

**POST** `/api/v1/tts`

Generate speech from text using advanced TTS with optional voice cloning and streaming response.

**Query Parameters:**
- `response_mode` (optional): Response mode - `"stream"` for direct file download, `"url"` for JSON response (default: `"stream"`)
- `return_format` (optional): Format to stream - `"wav"`, `"mp3"`, `"flac"`. If not specified, uses first format from export_formats

**Request Body:**
```json
{
  "text": "Hello, this is a test of the TTS API.",
  "reference_audio_filename": "speaker1/formal.wav",
  "exaggeration": 0.5,
  "temperature": 0.75,
  "seed": 42,
  "export_formats": ["wav", "mp3"]
}
```

**Response (JSON mode - when response_mode="url"):**
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_2025-06-20_143022_456_temp0.75_seed42.wav",
      "url": "/outputs/tts_2025-06-20_143022_456_temp0.75_seed42.wav",
      "path": "/path/to/outputs/tts_2025-06-20_143022_456_temp0.75_seed42.wav"
    },
    {
      "format": "mp3", 
      "filename": "tts_output_1234567890_42.mp3",
      "url": "/outputs/tts_output_1234567890_42.mp3"
    }
  ],
  "generation_seed_used": 42,
  "processing_time_seconds": 5.2,
  "message": "TTS generation completed successfully"
}
```

### 3. Voice Conversion

**POST** `/api/v1/vc`

Convert voice characteristics of input audio to match a target voice with support for direct file uploads and streaming response.

**Query Parameters:**
- `response_mode` (optional): Response mode - `"stream"` for direct file download, `"url"` for JSON response (default: `"stream"`)
- `return_format` (optional): Format to stream - `"wav"`, `"mp3"`, `"flac"`. If not specified, uses first format from export_formats

**Method 1: JSON Request with File References (traditional)**
> **Important**: Input files must be pre-placed in the `vc_inputs/` directory on the server

```json
{
  "input_audio_source": "recording.wav",        // Must exist in vc_inputs/ directory
  "target_voice_source": "speaker2.wav",        // Must exist in reference_audio/ directory
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "export_formats": ["wav", "mp3"]
}
```

**Method 2: Direct File Upload (multipart/form-data)**
> **Important**: Upload files directly in the request - no pre-staging required

- `input_audio`: File - Input audio file to convert (max 100MB, uploaded directly)
- `target_voice_source`: String - Target voice source (filename in reference_audio/ or URL)
- `chunk_sec`: Integer - Chunk size in seconds (default: 60)
- `overlap_sec`: Float - Overlap in seconds (default: 0.1)
- `disable_watermark`: Boolean - Disable watermark (default: true)
- `export_formats`: String - Comma-separated formats (default: "wav,mp3")

### **Key Differences:**
| Method | Input Audio | Target Voice | Use Case |
|--------|-------------|--------------|----------|
| **JSON** | Must be in `vc_inputs/` | Must be in `reference_audio/` | Server-side files, automation |
| **Upload** | Uploaded directly | Must be in `reference_audio/` | Client-side files, web apps |

**Response (JSON mode - when response_mode="url"):**
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "vc_2025-06-20_143045_789_chunk60_overlap0.1_voicespeaker2.wav",
      "url": "/outputs/vc_2025-06-20_143045_789_chunk60_overlap0.1_voicespeaker2.wav",
      "path": "/path/to/outputs/vc_2025-06-20_143045_789_chunk60_overlap0.1_voicespeaker2.wav"
    }
  ],
  "processing_time_seconds": 8.7,
  "message": "Voice conversion completed successfully"
}
```

**Response (Stream mode - when response_mode="stream"):**
Direct audio file download with proper Content-Disposition headers.
- **X-Alternative-Formats header**: Contains URLs to other formats (e.g., "mp3:/outputs/file.mp3|flac:/outputs/file.flac")

### 4. Configuration

**GET** `/api/v1/config`

Get API configuration and default values.

**Response:**
```json
{
  "tts_defaults": {
    "exaggeration": 0.5,
    "temperature": 0.75,
    "cfg_weight": 1.0,
    "seed": 0
  },
  "vc_defaults": {
    "chunk_sec": 60,
    "overlap_sec": 0.1
  },
  "supported_formats": ["wav", "mp3", "flac"],
  "api_limits": {
    "max_text_length": 10000,
    "download_timeout_seconds": 30
  }
}
```

### 5. Available Voices

**GET** `/api/v1/voices`

List available reference voice files with enhanced metadata, pagination, and search capabilities.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1, min: 1)
- `page_size` (integer, optional): Items per page (default: 50, max: 100)
- `search` (string, optional): Search term for voice names, descriptions, or tags
- `folder` (string, optional): Filter by folder path

**Example Request:**
```
GET /api/v1/voices?page=1&page_size=10&search=david&folder=speaker_en
```

**Response:**
```json
{
  "voices": [
    {
      "name": "DAVID-2",
      "description": "Voice file: DAVID-2.mp3",
      "duration_seconds": 83.91,
      "sample_rate": 44100,
      "file_size_bytes": 2015645,
      "format": "mp3",
      "default_parameters": {},
      "tags": [],
      "created_date": "2025-06-18T15:01:48.465839",
      "last_used": "2025-06-21T13:04:47.606227",
      "usage_count": 1,
      "folder_path": "speaker_en"
    }
  ],
  "count": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false
}
```

**Voice Metadata Fields:**
- `name`: Voice identifier (filename without extension)
- `description`: Human-readable description
- `duration_seconds`: Audio duration in seconds
- `sample_rate`: Audio sample rate (Hz)
- `file_size_bytes`: File size in bytes
- `format`: Audio format (wav, mp3, flac, etc.)
- `default_parameters`: Recommended TTS parameters for this voice
- `tags`: Array of descriptive tags
- `created_date`: ISO timestamp when voice was first added
- `last_used`: ISO timestamp when voice was last used
- `usage_count`: Number of times voice has been used
- `folder_path`: Relative folder path within reference_audio/ (null for root)

### Voice Management

#### Upload Voice File

**Endpoint:** `POST /api/v1/voice`  
**Description:** Upload a new voice file with metadata and folder organization

**Request Format:** `multipart/form-data`

**Form Fields:**
- `voice_file` (file, required): Voice audio file
- `name` (string, optional): Voice name (defaults to filename)
- `description` (string, optional): Voice description
- `tags` (string, optional): Comma-separated voice tags
- `folder_path` (string, optional): Folder organization path
- `default_parameters` (string, optional): JSON string of default TTS parameters
- `overwrite` (boolean, optional): Overwrite existing voice file (default: false)

**Example Request:**
```bash
curl -X POST http://localhost:7860/api/v1/voice \
  -F "voice_file=@my_voice.wav" \
  -F "name=My Custom Voice" \
  -F "description=A test voice for demonstrations" \
  -F "tags=test,custom,demo" \
  -F "folder_path=custom_voices"
```

#### Update Voice Metadata

**Endpoint:** `PUT /api/v1/voice/{filename}/metadata`  
**Description:** Update voice metadata without changing the audio file

#### Delete Single Voice

**Endpoint:** `DELETE /api/v1/voice/{filename}`  
**Description:** Delete a single voice file and its metadata
**Query Parameters:** `confirm=true` (required for safety)

#### Bulk Delete Voices

**Endpoint:** `DELETE /api/v1/voices`  
**Description:** Bulk delete voices based on criteria
**Query Parameters:** `confirm=true`, `folder`, `tag`, `search`, `filenames`

#### Get Voice Folder Structure

**Endpoint:** `GET /api/v1/voices/folders`  
**Description:** Get voice library folder structure and organization

### Generated Files Management

#### List Generated Files

**Endpoint:** `GET /api/v1/outputs`  
**Description:** List generated audio files with metadata, pagination, and search capabilities
**Query Parameters:** `page`, `page_size`, `generation_type`, `search`, `filenames`

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Referenced files missing |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Model loading failed |

### Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Invalid request parameters |
| `RESOURCE_NOT_FOUND` | Audio files not found |
| `MODEL_LOAD_ERROR` | AI model loading failed |
| `GENERATION_ERROR` | TTS/VC generation failed |
| `INTERNAL_ERROR` | Unexpected server error |

### Example Error Response

```json
{
  "success": false,
  "error": "Audio file not found: speaker1.wav in reference_audio",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2025-06-18T20:30:00Z"
}
```

## File Access

### Directory Structure

```
reference_audio/           # Reference voices for TTS and VC targets
├── speaker1/
│   ├── formal.wav
│   └── casual.wav
└── speaker2/
    └── energetic.wav

vc_inputs/                 # Source audio for voice conversion
├── recording1.wav
└── meeting_audio.mp3

outputs/                   # Generated results (HTTP accessible)
├── tts_output_xxx.wav
└── vc_output_xxx.mp3
```

### File Resolution

**TTS Reference Audio:**
- Looks in `reference_audio/` directory
- Supports subdirectories for organization
- Tries multiple extensions: `.wav`, `.mp3`, `.flac`

**VC Input Audio:**
- Local files: looks in `vc_inputs/` directory  
- URLs: downloads automatically to temp directory

**VC Target Audio:**
- Looks in `reference_audio/` directory (same as TTS)
- URLs supported for remote targets

### File Access URLs

Generated files are accessible via HTTP:
```
http://localhost:7860/outputs/tts_output_1234567890_42.wav
http://localhost:7860/outputs/vc_output_1234567890.mp3
```

## Advanced Features

### Text-to-Speech Advanced Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | **required** | Text to synthesize |
| `reference_audio_filename` | string | null | Voice reference file |
| `exaggeration` | float | 0.5 | Voice expressiveness (0.0-1.0) |
| `temperature` | float | 0.75 | Generation randomness |
| `seed` | integer | 0 | Random seed (0 = random) |
| `cfg_weight` | float | 1.0 | Classifier-free guidance weight |
| `num_candidates_per_chunk` | integer | 3 | Generation candidates |
| `max_attempts_per_candidate` | integer | 3 | Retry attempts |
| `bypass_whisper_checking` | boolean | false | Skip quality validation |
| `whisper_model_name` | string | "medium" | Whisper model size |
| `use_faster_whisper` | boolean | true | Use faster-whisper backend |
| `enable_batching` | boolean | false | Enable text batching |
| `smart_batch_short_sentences` | boolean | true | Smart sentence grouping |
| `to_lowercase` | boolean | true | Convert text to lowercase |
| `normalize_spacing` | boolean | true | Normalize whitespace |
| `fix_dot_letters` | boolean | true | Fix letter.dot.sequences |
| `remove_reference_numbers` | boolean | true | Remove [1], (2) patterns |
| `export_formats` | array | ["wav","mp3"] | Output formats |
| `disable_watermark` | boolean | true | Disable audio watermark |

### Voice Conversion Advanced Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_audio_source` | string | **required** | Source audio file/URL |
| `target_voice_source` | string | **required** | Target voice file/URL |
| `chunk_sec` | integer | 60 | Chunk duration in seconds |
| `overlap_sec` | float | 0.1 | Overlap for seamless joining |
| `export_formats` | array | ["wav","mp3"] | Output formats |
| `disable_watermark` | boolean | true | Disable audio watermark |

### Whisper Quality Validation

When `bypass_whisper_checking` is `false` (default), the API:
1. **Generates multiple candidates** for each text chunk
2. **Transcribes each candidate** using Whisper 
3. **Compares transcription** to original text
4. **Selects best candidates** (similarity ≥ 95%)
5. **Retries failed chunks** up to max attempts
6. **Falls back gracefully** for persistent failures

### Chunking & Parallel Processing

**TTS Chunking:**
- Long texts are split into sentences
- Sentences grouped using smart batching
- Each chunk processed independently
- Results combined seamlessly

**VC Chunking:**
- Long audio split into overlapping chunks
- Crossfading applied for smooth transitions
- Configurable chunk size and overlap

## Configuration

### Environment Setup

The API reads configuration from `config.yaml`:

```yaml
# Server settings
server:
  host: "127.0.0.1"
  port: 7860
  log_level: "INFO"

# Path configuration  
paths:
  reference_audio_dir: "reference_audio"
  vc_input_dir: "vc_inputs"
  output_dir: "outputs"
  temp_dir: "temp"

# Model settings
models:
  device: "auto"  # auto, cuda, cpu
  preload_models: true

# API settings
api:
  max_text_length: 10000
  cleanup_temp_files: true
  enable_url_downloads: true
  download_timeout_seconds: 30
```

### Model Management

The API automatically:
- **Detects optimal device** (CUDA/CPU)
- **Loads models on-demand** or at startup
- **Manages model memory** efficiently
- **Handles model failures** gracefully

## Examples

### Basic TTS Generation

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a basic TTS example.",
    "export_formats": ["wav"]
  }'
```

### TTS with Voice Cloning

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This text will be spoken in the reference voice style.",
    "reference_audio_filename": "speaker1/formal.wav",
    "exaggeration": 0.7,
    "temperature": 0.8,
    "export_formats": ["wav", "mp3"]
  }'
```

### TTS with Enhanced Speed Control

```bash
# High-quality speed adjustment with audiostretchy
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This demonstrates high-quality speed adjustment with enhanced libraries.",
    "reference_audio_filename": "speaker1/formal.wav",
    "speed_factor": 1.5,
    "speed_factor_library": "audiostretchy",
    "export_formats": ["wav"]
  }'

# Auto library selection based on speed range
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Automatic library selection for optimal quality.",
    "speed_factor": 0.8,
    "speed_factor_library": "auto",
    "export_formats": ["wav"]
  }'
```

**Speed Factor Libraries:**
- `auto` - Smart selection with audiostretchy preferred for speech quality (recommended)
- `audiostretchy` - TDHS algorithm, superior speech quality with formant preservation
- `librosa` - Good baseline compatibility with adequate quality
- `torchaudio` - Basic fallback (affects pitch, use only when others unavailable)

### Voice Conversion with Local Files

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "my_recording.wav",
    "target_voice_source": "target_voices/celebrity.wav",
    "chunk_sec": 30,
    "export_formats": ["wav"]
  }'
```

### Voice Conversion with URLs

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "https://example.com/speech.wav",
    "target_voice_source": "speaker2/style.wav",
    "export_formats": ["wav", "mp3"]
  }'
```

### Python Client Example

```python
import requests
import json

# TTS Generation
def generate_tts(text, reference_voice=None):
    payload = {
        "text": text,
        "export_formats": ["wav", "mp3"]
    }
    if reference_voice:
        payload["reference_audio_filename"] = reference_voice
    
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Generated {len(result['output_files'])} files:")
        for file_info in result['output_files']:
            print(f"  - {file_info['format']}: {file_info['url']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Voice Conversion
def convert_voice(input_file, target_voice):
    payload = {
        "input_audio_source": input_file,
        "target_voice_source": target_voice,
        "export_formats": ["wav"]
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/vc",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Conversion completed in {result['processing_time_seconds']:.1f}s")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Usage
generate_tts("Hello world!", "speaker1/formal.wav")
convert_voice("recording.wav", "target_voice.wav")
```

### JavaScript/Node.js Client Example

```javascript
// TTS Generation
async function generateTTS(text, referenceVoice = null) {
    const payload = {
        text: text,
        export_formats: ["wav", "mp3"]
    };
    
    if (referenceVoice) {
        payload.reference_audio_filename = referenceVoice;
    }
    
    try {
        const response = await fetch('http://localhost:7860/api/v1/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`Generated ${result.output_files.length} files:`);
            result.output_files.forEach(file => {
                console.log(`  - ${file.format}: ${file.url}`);
            });
            return result;
        } else {
            const error = await response.json();
            console.error('Error:', error);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Voice Conversion
async function convertVoice(inputFile, targetVoice) {
    const payload = {
        input_audio_source: inputFile,
        target_voice_source: targetVoice,
        export_formats: ["wav"]
    };
    
    try {
        const response = await fetch('http://localhost:7860/api/v1/vc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`Conversion completed in ${result.processing_time_seconds.toFixed(1)}s`);
            return result;
        } else {
            const error = await response.json();
            console.error('Error:', error);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Usage
generateTTS("Hello world!", "speaker1/formal.wav");
convertVoice("recording.wav", "target_voice.wav");
```

## Phase 9 Enhanced Features

### Streaming Responses

Both TTS and VC endpoints now support direct file streaming for immediate downloads:

```bash
# Get TTS as direct download (default behavior - WAV format)
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav", "mp3"]}' \
  --output speech.wav

# Get TTS as MP3 download (specify return format)
curl -X POST "http://localhost:7860/api/v1/tts?return_format=mp3" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav", "mp3"]}' \
  --output speech.mp3

# Get JSON response with URLs (legacy mode)
curl -X POST "http://localhost:7860/api/v1/tts?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav"]}'
```

### Direct File Upload for Voice Conversion

Upload audio files directly to the VC endpoint:

```bash
# Upload file with curl
curl -X POST http://localhost:7860/api/v1/vc \
  -F "input_audio=@my_recording.wav" \
  -F "target_voice_source=speaker1.wav" \
  -F "chunk_sec=30" \
  -F "export_formats=wav,mp3" \
  --output converted_voice.wav
```

### Enhanced File Naming

Generated files now include meaningful parameters in their names:

- **TTS files:** `tts_2025-06-20_143022_456_temp0.75_seed42.wav`
- **VC files:** `vc_2025-06-20_143045_789_chunk60_overlap0.1_voicespeaker2.wav`
- **Metadata:** Each generated file has a companion `.json` file with complete generation context

### Python Examples for New Features

```python
import requests

# Streaming TTS (direct download)
def download_tts_direct(text, output_path="speech.wav"):
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json={"text": text, "export_formats": ["wav"]},
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {output_path}")
    else:
        print(f"Error: {response.status_code}")

# File upload VC (direct upload)
def upload_vc_conversion(audio_file_path, target_voice, output_path="converted.wav"):
    """Upload audio file directly for conversion"""
    with open(audio_file_path, 'rb') as audio_file:
        files = {'input_audio': audio_file}
        data = {
            'target_voice_source': target_voice,  # Must exist in reference_audio/
            'chunk_sec': 30,
            'export_formats': 'wav'
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/vc",
            files=files,
            data=data,
            stream=True
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Converted and downloaded: {output_path}")
        else:
            print(f"Error: {response.status_code}")

# JSON VC (server-side files)
def json_vc_conversion(input_filename, target_voice, output_path="converted.wav"):
    """Convert using files already on server"""
    # Note: input_filename must exist in vc_inputs/ directory on server
    payload = {
        'input_audio_source': input_filename,    # Must be in vc_inputs/
        'target_voice_source': target_voice,     # Must be in reference_audio/
        'chunk_sec': 30,
        'export_formats': ['wav']
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/vc",
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Converted and downloaded: {output_path}")
    else:
        print(f"Error: {response.status_code}")

# Usage examples
upload_vc_conversion("my_recording.wav", "speaker1.wav")      # Upload mode
json_vc_conversion("server_file.wav", "speaker1.wav")        # JSON mode (file must be in vc_inputs/)
```

---

## Support & Development

- **Project Repository:** [Chatterbox-TTS-Extended-Plus](https://github.com/your-repo)
- **Issues & Bugs:** Use GitHub Issues for bug reports
- **API Version:** 1.0.0 
- **Last Updated:** June 18, 2025

For technical questions about the underlying models, refer to the Chatterbox documentation.

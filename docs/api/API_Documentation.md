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
| `/api/v1/voices` | GET | Available reference voices |

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

Generate speech from text using advanced TTS with optional voice cloning.

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

**Response:**
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_output_1234567890_42.wav",
      "url": "/outputs/tts_output_1234567890_42.wav"
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

Convert voice characteristics of input audio to match a target voice.

**Request Body:**
```json
{
  "input_audio_source": "recording.wav",
  "target_voice_source": "target_voices/speaker2.wav", 
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "export_formats": ["wav", "mp3"]
}
```

**Response:**
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "vc_output_1234567890.wav",
      "url": "/outputs/vc_output_1234567890.wav"
    }
  ],
  "processing_time_seconds": 8.7,
  "message": "Voice conversion completed successfully"
}
```

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

List available reference voice files.

**Response:**
```json
{
  "voices": [
    {"path": "speaker1/formal.wav"},
    {"path": "speaker1/casual.wav"}, 
    {"path": "speaker2/energetic.wav"}
  ]
}
```

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

---

## Support & Development

- **Project Repository:** [Chatterbox-TTS-Extended-Plus](https://github.com/your-repo)
- **Issues & Bugs:** Use GitHub Issues for bug reports
- **API Version:** 1.0.0 
- **Last Updated:** June 18, 2025

For technical questions about the underlying models, refer to the Chatterbox documentation.

# 🚀 Chatterbox-TTS-Extended-Plus API

This document describes how to use the FastAPI-based HTTP API interface for Chatterbox-TTS-Extended-Plus, which provides programmatic access to advanced Text-to-Speech (TTS) and Voice Conversion (VC) capabilities.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Features](#api-features)
- [Starting the API Server](#starting-the-api-server)
- [API Access Points](#api-access-points)
- [Basic Usage Examples](#basic-usage-examples)
- [Audio File Organization](#audio-file-organization)
- [Supported Audio Formats](#supported-audio-formats)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Documentation & Testing](#documentation--testing)

---

## Quick Start

1. **Start the API server:**
   ```bash
   python main_api.py
   ```

2. **Access the services:**
   - **API Endpoints:** `http://localhost:7860/api/v1/`
   - **Gradio UI:** `http://localhost:7860/ui` (original interface)
   - **API Documentation:** `http://localhost:7860/docs` (interactive)

3. **Test with a simple TTS request:**
   ```bash
   curl -X POST "http://localhost:7860/api/v1/tts" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test!"}'
   ```

---

## API Features

### 🎤 Text-to-Speech (TTS)
- **Endpoint:** `POST /api/v1/tts`
- High-quality speech synthesis with customizable parameters
- Reference audio support for voice cloning
- Advanced text preprocessing and validation
- Multiple output formats (WAV, MP3, FLAC)
- Comprehensive error handling and validation

### 🔄 Voice Conversion (VC)
- **Endpoint:** `POST /api/v1/vc`
- Convert any voice to sound like another
- Support for local files and URL downloads
- Automatic chunking for long audio files
- Crossfade processing for seamless results

### 🔧 Utility Endpoints
- **Health Check:** `GET /api/v1/health` - Server status and metrics
- **Configuration:** `GET /api/v1/config` - Current settings and defaults
- **Voice List:** `GET /api/v1/voices` - Available reference voices
- **Resource Status:** `GET /api/v1/resources` - Disk usage and cleanup status
- **Error Tracking:** `GET /api/v1/errors/summary` - Error monitoring

---

## Starting the API Server

The API server provides both the HTTP API and the original Gradio UI:

```bash
# Standard startup
python main_api.py

# Custom host/port
python main_api.py --host 0.0.0.0 --port 8000

# Production mode (see deployment guide)
uvicorn main_api:app --host 127.0.0.1 --port 7860
```

**Server Configuration:**
- Default host: `127.0.0.1` (localhost only)
- Default port: `7860`
- Configuration file: `config.yaml`
- Logs directory: `logs/`

---

## API Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **API Base** | `http://localhost:7860/api/v1/` | REST API endpoints |
| **UI Interface** | `http://localhost:7860/ui` | Original Gradio interface |
| **Documentation** | `http://localhost:7860/docs` | Interactive API docs (Swagger) |
| **OpenAPI Spec** | `http://localhost:7860/openapi.json` | Machine-readable API spec |
| **Audio Files** | `http://localhost:7860/outputs/` | Generated audio downloads |

---

## Basic Usage Examples

### Text-to-Speech Generation
```bash
# Simple TTS
curl -X POST "http://localhost:7860/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world! This is a test of the TTS system.",
    "export_formats": ["wav", "mp3"]
  }'

# TTS with reference voice
curl -X POST "http://localhost:7860/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world!",
    "reference_audio_filename": "my_voice.wav",
    "temperature": 0.8,
    "export_formats": ["wav", "mp3"]
  }'
```

### Voice Conversion
```bash
# Convert local audio files
curl -X POST "http://localhost:7860/api/v1/vc" \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "source_audio.wav",
    "target_voice_source": "target_voice.wav",
    "export_formats": ["wav", "mp3"]
  }'

# Convert with URL download
curl -X POST "http://localhost:7860/api/v1/vc" \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "https://example.com/audio.mp3",
    "target_voice_source": "local_target.wav",
    "export_formats": ["wav"]
  }'
```

### Utility Endpoints
```bash
# Check server health
curl "http://localhost:7860/api/v1/health"

# Get available voices
curl "http://localhost:7860/api/v1/voices"

# Get configuration
curl "http://localhost:7860/api/v1/config"
```

---

## Audio File Organization

The API uses a structured directory system for audio files:

```
project_root/
├── reference_audio/          # Reference voices (TTS + VC targets)
│   ├── tts_voices/          # TTS-specific reference voices
│   ├── vc_targets/          # VC-specific target voices
│   └── shared/              # Voices for both TTS and VC
├── vc_inputs/               # Input audio for voice conversion
├── outputs/                 # Generated audio files (accessible via HTTP)
└── temp/                    # Temporary files (URLs, processing)
```

### File Resolution
- **TTS reference:** Looks in `reference_audio/` directory and subdirectories
- **VC input:** Looks in `vc_inputs/` directory for source audio
- **VC target:** Looks in `reference_audio/` directory for target voices
- **URLs:** Automatically downloaded to `temp/` directory
- **Outputs:** Saved to `outputs/` and accessible via HTTP URLs

---

## Supported Audio Formats

### Input Formats
- **WAV** - Uncompressed (preferred)
- **MP3** - Compressed audio
- **FLAC** - Lossless compression
- **M4A, OGG** - Additional formats

### Output Formats
- **WAV** - Uncompressed, highest quality
- **MP3** - 320kbps, good balance of quality/size
- **FLAC** - Lossless compression, smaller than WAV

**Format Selection:**
```json
{
  "text": "Hello world",
  "export_formats": ["wav", "mp3", "flac"]  // Choose any combination
}
```

---

## Error Handling

The API provides comprehensive error handling with specific error codes:

### Error Response Format
```json
{
  "success": false,
  "error": "Descriptive error message",
  "detail": "Technical details for debugging",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-19T10:30:00Z"
}
```

### Common Error Codes
- **`VALIDATION_ERROR`** (400) - Invalid input parameters
- **`RESOURCE_NOT_FOUND`** (404) - Audio file not found
- **`MODEL_LOAD_ERROR`** (503) - AI model loading failed
- **`GENERATION_ERROR`** (500) - TTS/VC generation failed
- **`INTERNAL_ERROR`** (500) - Unexpected server error

### Error Monitoring
```bash
# Get error summary
curl "http://localhost:7860/api/v1/errors/summary"

# Get recent errors
curl "http://localhost:7860/api/v1/errors/recent?limit=10"
```

---

## Performance Considerations

### Resource Management
- **Disk Space:** Automatic cleanup of old files
- **Memory:** Efficient model loading and caching
- **CUDA:** GPU memory management for AI models

### Processing Time
- **TTS:** ~1-2 minutes for typical text (depends on length and complexity)
- **VC:** ~30 seconds to several minutes (depends on audio length)
- **Parallel Processing:** Multiple requests are queued and processed sequentially

### Optimization Tips
- Use WAV format for inputs when possible (faster processing)
- Keep reference audio files under 30 seconds for best results
- Monitor disk space in `outputs/` directory
- Use the health endpoint to monitor system resources

---

## Documentation & Testing

### Interactive Documentation
- **Swagger UI:** `http://localhost:7860/docs`
- **ReDoc:** `http://localhost:7860/redoc`
- **OpenAPI Spec:** `http://localhost:7860/openapi.json`

### Testing Tools
```bash
# Test basic functionality
python tests/test_api_endpoints.py

# Performance testing
python tests/test_performance_fix.py
```

### Client Libraries
- **Python:** Use `requests` or `httpx` libraries
- **JavaScript:** Standard `fetch()` API or axios
- **cURL:** Command-line testing and scripting

### Example Python Client
```python
import requests

# TTS Generation
response = requests.post(
    "http://localhost:7860/api/v1/tts",
    json={
        "text": "Hello, world!",
        "export_formats": ["wav", "mp3"]
    }
)

if response.status_code == 200:
    result = response.json()
    print("Generated files:", result["output_files"])
else:
    print("Error:", response.json())
```

---

## Additional Resources

- **📖 Full API Documentation:** `docs/API_Documentation.md`
- **🚀 Deployment Guide:** `docs/Deployment_Guide.md`
- **🔧 Configuration Reference:** `config.yaml`
- **📊 Monitoring Guide:** `docs/monitoring/`
- **🐛 Error Tracking:** `docs/monitoring/Monitoring_User_Guide.md`

---

## Support & Troubleshooting

For issues with the API:

1. Check the **health endpoint** for system status
2. Review **logs** in the `logs/` directory  
3. Consult the **error summary** endpoint for recent issues
4. See the **full documentation** in `docs/API_Documentation.md`
5. Test with the **original Gradio UI** at `/ui` to isolate API issues

The API maintains full compatibility with the original Chatterbox-TTS-Extended functionality while providing modern HTTP API access for integration and automation.

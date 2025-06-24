# Quick Start Guide

Get up and running with Chatterbox TTS Extended Plus API in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- At least 4GB of RAM
- GPU recommended (but not required)

## Installation and Setup

### 1. Start the Server

Navigate to your Chatterbox TTS Extended Plus directory and start the API server:

```bash
python main_api.py
```

The server will start on http://localhost:7860

### 2. Verify Installation

Test that the API is running:

```bash
curl http://localhost:7860/api/v1/health
```

Expected response:
```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

### 3. Setup Validation (Two-Tier Testing)

The API supports two levels of functionality testing:

#### **Core Validation (Always Available)**
These examples work immediately without any voice file setup:

```bash
# Test basic functionality (should always work)
curl http://localhost:7860/api/v1/voices
curl -X POST http://localhost:7860/api/v1/tts -H "Content-Type: application/json" -d '{"text": "Hello world", "export_formats": ["wav"]}'
```

#### **Advanced Validation (Requires Setup)**
For advanced features, verify that test voice files are available:

```bash
# Check for required test voice files
curl http://localhost:7860/api/v1/voices | grep -E "(linda_johnson|test_voices)"
```

**Expected output should include:**
- `test_voices/linda_johnson_01.mp3`
- `test_voices/linda_johnson_02.mp3`

If these files are missing, you'll need to add them for advanced examples to work. See [Voice File Setup](#voice-file-setup) section below.

## Your First API Calls

### Core Examples (Universal - No Setup Required)

These examples work on any installation without requiring specific voice files:

#### Basic Text-to-Speech
Generate speech from text using the default voice:

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is my first TTS generation!",
    "export_formats": ["wav", "mp3"]
  }'
```

#### Basic Voice Conversion (Using Project Test Files)
Transform an existing audio file (if available):

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "test_inputs/chatterbox-hello_quick_brown.wav",
    "target_voice_source": "test_voices/linda_johnson_01.mp3",
    "export_formats": ["wav"]
  }'
```

### Advanced Examples (Requires Voice File Setup)

These examples require the test voice files described in [Voice File Setup](#voice-file-setup):

#### TTS with Voice Cloning
Use a reference voice for more personalized speech:

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This will sound like the reference speaker.",
    "reference_audio_filename": "test_voices/linda_johnson_02.mp3",
    "export_formats": ["wav"]
  }'
```

#### Advanced Voice Conversion
Transform using different voice files:

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "test_inputs/chatterbox-in-a-village-of-la-mancha.mp3",
    "target_voice_source": "test_voices/linda_johnson_02.mp3",
    "export_formats": ["wav"]
  }'
```

## Understanding the Response

All successful API calls return structured JSON responses:

```json
{
  "success": true,
  "message": "Generation completed successfully",
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_2025-06-22_143022_456.wav",
      "url": "/outputs/tts_2025-06-22_143022_456.wav",
      "path": "/full/path/to/outputs/tts_2025-06-22_143022_456.wav"
    }
  ],
  "processing_time_seconds": 2.3,
  "timestamp": "2025-06-22T14:30:22Z"
}
```

## Accessing Generated Files

### Direct Download

Use the URL from the response to download files:

```bash
# Download the generated audio file
curl -O http://localhost:7860/outputs/tts_2025-06-22_143022_456.wav
```

### List All Generated Files

See all your generated audio files:

```bash
curl http://localhost:7860/api/v1/outputs
```

## File Organization

The API expects files to be organized in specific directories:

```
project_root/
├── reference_audio/     # Voice reference files (for TTS and VC targets)
├── vc_inputs/          # Source audio files for voice conversion
├── outputs/            # Generated audio files
└── temp/               # Temporary downloads and processing
```

## Voice File Setup

### Basic Setup (Core Examples)
Core examples work without specific voice files and use the default voice system.

### Advanced Setup (Full Examples)
For advanced features and comprehensive testing, you need specific test voice files:

#### **Required Files for Advanced Examples:**

**Reference voices** (place in `reference_audio/test_voices/`):
- `linda_johnson_01.mp3` - Primary test voice for TTS and VC
- `linda_johnson_02.mp3` - Secondary test voice for advanced examples

**VC input files** (place in `vc_inputs/test_inputs/`):
- `chatterbox-hello_quick_brown.wav` - Short test audio for VC
- `chatterbox-in-a-village-of-la-mancha.mp3` - Longer test audio

#### **Setup Verification Commands:**

```bash
# Verify voice files are properly set up
curl http://localhost:7860/api/v1/voices | grep -E "(linda_johnson|test_voices)"

# Check that VC input files are available (they won't show in API responses)
# You can verify manually that files exist in vc_inputs/test_inputs/
```

#### **If Files Are Missing:**
- **Core examples** will still work (they don't require specific voice files)
- **Advanced examples** may fail with "file not found" errors
- You can substitute your own audio files by updating the filenames in examples

### Setting Up Your Own Audio Files

1. **For TTS voice cloning:** Place reference voice files in `reference_audio/`
2. **For voice conversion:** Place source audio in `vc_inputs/` and target voices in `reference_audio/`

**Recommended audio specifications:**
- **Format**: WAV, MP3, or FLAC
- **Duration**: 10-30 seconds for reference voices
- **Quality**: Clean speech, minimal background noise
- **Sample rate**: 22kHz or 44.1kHz

## Basic Python Integration

```python
import requests

# Simple TTS function
def generate_speech(text, voice_file=None):
    payload = {
        "text": text,
        "export_formats": ["wav", "mp3"]
    }
    if voice_file:
        payload["reference_audio_filename"] = voice_file
    
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Generated files:")
        for file_info in result['output_files']:
            print(f"  {file_info['format']}: {file_info['url']}")
        return result
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
generate_speech("Hello world!")
generate_speech("Custom voice test", "test_voices/linda_johnson_01.mp3")
```

## Common Issues and Solutions

### Server Won't Start
- **Check Python version:** Ensure Python 3.8+
- **Check dependencies:** Run `pip install -r requirements.txt`
- **Port conflicts:** Change port in `config.yaml` if 7860 is in use

### "File Not Found" Errors
- **Check file paths:** Ensure audio files are in correct directories
- **File extensions:** API supports .wav, .mp3, .flac formats
- **Case sensitivity:** Filenames are case-sensitive on Linux/Mac

### Poor Audio Quality
- **Use clean reference audio:** 10-30 seconds of clear speech
- **Check sample rates:** 22kHz or 44.1kHz recommended
- **Adjust parameters:** Try different temperature and exaggeration values

### Slow Processing
- **GPU acceleration:** Ensure CUDA is available for faster processing
- **Chunk size:** For long audio, adjust `chunk_sec` parameter
- **Model preloading:** Set `preload_models: true` in config.yaml

## Next Steps

### Explore Advanced Features
- **[Speed Control](guides/advanced-features.md#speed-control)** - Adjust playback speed while preserving quality
- **[File Uploads](guides/file-uploads.md)** - Upload audio files directly in API requests
- **[Streaming Responses](guides/streaming-responses.md)** - Get files directly without URLs

### Detailed Documentation
- **[TTS Endpoint](endpoints/tts.md)** - Complete TTS API reference
- **[Voice Conversion](endpoints/voice-conversion.md)** - Full VC documentation
- **[Configuration](reference/configuration.md)** - Server and model settings

### Integration Examples
- **[Python Examples](schemas/examples/python-examples.md)** - Comprehensive Python integration
- **[cURL Examples](schemas/examples/curl-examples.md)** - Two-tier command-line usage patterns
  - **Core Examples**: Universal validation (2-3 minutes)
  - **Advanced Examples**: Comprehensive testing (8-15 minutes)

## Interactive Documentation

For hands-on exploration, visit the interactive API documentation:
- **Swagger UI:** http://localhost:7860/docs
- **ReDoc:** http://localhost:7860/redoc

---

*Having trouble? Check our [Error Handling Guide](guides/error-handling.md) or review the complete [API Documentation](README.md)*
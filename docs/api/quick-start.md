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

## Your First API Calls

### Text-to-Speech (TTS)

Generate speech from text using the default voice:

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is my first TTS generation!",
    "export_formats": ["wav", "mp3"]
  }'
```

#### With Voice Cloning

Use a reference voice for more personalized speech:

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This will sound like the reference speaker.",
    "reference_audio_filename": "speaker1.wav",
    "export_formats": ["wav"]
  }'
```

### Voice Conversion (VC)

Transform an existing audio file to sound like a different speaker:

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "my_recording.wav",
    "target_voice_source": "target_speaker.wav",
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

### Setting Up Audio Files

1. **For TTS voice cloning:** Place reference voice files in `reference_audio/`
2. **For voice conversion:** Place source audio in `vc_inputs/` and target voices in `reference_audio/`

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
generate_speech("Custom voice test", "my_voice.wav")
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
- **[cURL Examples](schemas/examples/curl-examples.md)** - Command-line usage patterns

## Interactive Documentation

For hands-on exploration, visit the interactive API documentation:
- **Swagger UI:** http://localhost:7860/docs
- **ReDoc:** http://localhost:7860/redoc

---

*Having trouble? Check our [Error Handling Guide](guides/error-handling.md) or review the complete [API Documentation](README.md)*
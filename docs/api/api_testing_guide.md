# API Testing Guide - Phase 3 Completion

## Current Status
✅ **Phase 3: Basic API Implementation - COMPLETED**

All core API endpoints have been implemented and basic functionality tests are passing. The API server is ready for manual testing.

## Quick Start

### 1. Start the API Server
```bash
cd "E:\Repos\Chatterbox-TTS-Extended-Plus"
.venv\Scripts\python.exe main_api.py
```

The server will start on `http://127.0.0.1:7860`

### 2. Test Health Endpoint
```bash
curl http://127.0.0.1:7860/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "models_loaded": {"tts": false, "vc": false},
  "version": "1.2.0",
  "uptime_seconds": 123.45
}
```

### 3. Test Configuration Endpoint
```bash
curl http://127.0.0.1:7860/api/v1/config
```

### 4. Test Voice Listing
```bash
curl http://127.0.0.1:7860/api/v1/voices
```

### 5. Test TTS Endpoint (Basic)
```bash
curl -X POST http://127.0.0.1:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the TTS API",
    "export_formats": ["wav", "mp3"]
  }'
```

### 6. Test VC Endpoint (requires audio files)
**Note:** This requires audio files to be placed in the appropriate directories first.

```bash
curl -X POST http://127.0.0.1:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "test_input.wav",
    "target_voice_source": "test_target.wav",
    "export_formats": ["wav", "mp3"]
  }'
```

## API Documentation

Look at the full [API documentation](API_Documentation.md).
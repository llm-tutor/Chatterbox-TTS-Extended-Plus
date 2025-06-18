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

### Available Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/config` - Configuration info
- `GET /api/v1/voices` - List available voices
- `POST /api/v1/tts` - Text-to-Speech generation
- `POST /api/v1/vc` - Voice conversion
- `GET /outputs/{filename}` - Download generated files

### Error Codes

- `400` - Validation Error (bad request parameters)
- `404` - Resource Not Found (audio files, etc.)
- `500` - Generation Error (TTS/VC processing failed)
- `503` - Model Load Error (models not available)

## What Works Now

✅ **Basic API Structure**
- FastAPI application with all endpoints
- Error handling and validation
- Static file serving for outputs
- Configuration management

✅ **Core Logic Integration**
- CoreEngine integrated with API endpoints
- Model loading and device detection
- Basic TTS and VC generation logic
- Multi-format audio conversion

✅ **Testing Infrastructure**
- Basic functionality tests passing
- Import validation working
- Configuration loading verified

## What's Next (Phase 4)

🔲 **Enhanced Features (Not Yet Implemented)**
- Full URL download support for audio files
- Complete multi-format audio conversion pipeline
- Enhanced utility endpoints
- Improved error handling and responses
- Request validation and sanitization

## Testing Notes

1. **Models Loading**: Models will load automatically when first endpoint is called
2. **CUDA Support**: Device detection shows "cuda" if available
3. **Audio Files**: For VC testing, you'll need to place audio files in:
   - `reference_audio/` for target voices
   - `vc_inputs/` for source audio
4. **Generated Files**: Outputs will be saved to `outputs/` directory

## Commit Status

This represents the completion of Phase 3. All basic API functionality is implemented and ready for testing. Once you confirm the API works as expected, we can proceed to Phase 4 for enhanced features.

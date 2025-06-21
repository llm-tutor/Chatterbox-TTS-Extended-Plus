# Phase 9 Test Clients

This folder contains comprehensive test clients for the Phase 9 Enhanced Features:

## Files

- `test_tts_client.py` - TTS test client with streaming and format selection
- `test_vc_client.py` - Voice Conversion test client with file upload and streaming  
- `media/` - Directory for input/output audio files

## Setup

1. **Start the API server**:
   ```bash
   cd E:\Repos\Chatterbox-TTS-Extended-Plus
   python main_api.py
   ```

2. **Prepare test files**:
   - Copy your input audio file for VC testing to `tests/media/`
   - Update the filename in `test_vc_client.py` (search for `input_recording.wav`)

## Running Tests

### TTS Tests
```bash
cd tests
python test_tts_client.py
```

**Features tested**:
- Basic streaming (WAV)
- Multi-format with MP3 streaming
- JSON response mode
- Reference audio cloning
- Enhanced parameters

### VC Tests  
```bash
cd tests
python test_vc_client.py
```

**Features tested**:
- JSON mode streaming (traditional)
- JSON mode with format selection
- JSON mode URL response
- File upload streaming (new!)
- File upload with FLAC format
- File upload JSON response

## Expected Output

### Enhanced Filename Patterns
- TTS: `tts_test_1703123456_temp0.75_seed42.wav`
- VC: `vc_upload_test_1703123456_chunk60.mp3`

### Response Headers (Streaming)
```
Content-Disposition: attachment; filename="enhanced_name.wav"
X-Alternative-Formats: mp3:/outputs/file.mp3|flac:/outputs/file.flac
```

### Format Selection Logic
- `return_format=mp3` → Streams MP3 file
- `return_format=unknown` → Falls back to first available format
- No `return_format` → Uses first format from `export_formats`

## Notes

- Update `input_recording.wav` placeholder with your actual test file name
- Files are saved to `tests/media/` with enhanced naming patterns
- Check console output for alternative format URLs when streaming

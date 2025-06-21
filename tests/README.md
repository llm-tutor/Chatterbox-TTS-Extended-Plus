# Test Clients - Phases 9 & 10

This folder contains comprehensive test clients for the Enhanced Features:

## Files

### Phase 9 Tests (Core Response & Upload Enhancement)
- `test_tts_client.py` - TTS test client with streaming and format selection
- `test_vc_client.py` - Voice Conversion test client with file upload and streaming  

### Phase 10 Tests (Speed Control & Voice Metadata)
- `test_phase10_tasks_10_1_10_2.py` - Complete Phase 10 test suite (Tasks 10.1 & 10.2)
- `test_voice_metadata_validation.py` - Deep voice metadata accuracy validation

### Directories
- `media/` - Directory for input/output audio files (includes speed test files)

## Setup

1. **Start the API server**:
   ```bash
   cd E:\Repos\Chatterbox-TTS-Extended-Plus
   python main_api.py
   ```

2. **Prepare test files**:
   - Copy your input audio file for VC testing to `tests/media/`
   - Update the filename in `test_vc_client.py` (search for `input_recording.wav`)
   - Ensure voice files exist in `reference_audio/` for metadata tests

## Running Tests

### Phase 9 - Enhanced Features

#### TTS Tests
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

#### VC Tests  
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

### Phase 10 - Speed Control & Voice Metadata

#### Complete Phase 10 Test Suite
```bash
cd tests
python test_phase10_tasks_10_1_10_2.py
```

**Features tested**:
- **Task 10.1**: Speed factors 0.5x, 1.0x, 1.5x, 2.0x (quality issues noted)
- **Task 10.2**: Voice metadata API with pagination and search
- Voice usage tracking for both TTS and VC
- Enhanced API responses with rich metadata
- Files saved with timestamps to avoid overwriting

#### Voice Metadata Deep Validation
```bash
cd tests
python test_voice_metadata_validation.py
```

**Features tested**:
- Metadata calculation accuracy (duration, sample rate, file size)
- JSON companion files validation in `reference_audio/`
- API consistency with file metadata
- Usage tracking for both TTS and VC endpoints

## Expected Output

### Enhanced Filename Patterns
- **TTS**: `tts_2025-06-21_143022_456_temp0.75_seed42_speed1.5.wav`
- **VC**: `vc_2025-06-21_143045_789_chunk60_overlap0.1_voicespeaker2.wav`
- **Phase 10 Tests**: `phase10_speed_1.5x_20250621_143022.wav`

### Response Headers (Streaming)
```
Content-Disposition: attachment; filename="enhanced_name.wav"
X-Alternative-Formats: mp3:/outputs/file.mp3|flac:/outputs/file.flac
```

### Voice Metadata API Response
```json
{
  "voices": [
    {
      "name": "speaker1",
      "duration_seconds": 12.5,
      "sample_rate": 22050,
      "file_size_bytes": 276480,
      "usage_count": 5,
      "last_used": "2025-06-21T14:30:22Z",
      "folder_path": null
    }
  ],
  "page": 1,
  "total_pages": 1,
  "has_next": false
}
```

## Format Selection Logic
- `return_format=mp3` → Streams MP3 file
- `return_format=unknown` → Falls back to first available format
- No `return_format` → Uses first format from `export_formats`

## Voice Metadata Features
- **Auto-calculation**: Duration, sample rate, file size
- **JSON companions**: `.wav.json` files created automatically
- **Usage tracking**: Counts increment when voices are used in TTS or VC
- **API pagination**: `?page=1&page_size=5&search=term`

## Known Issues

### Speed Factor (Task 10.1)
- **Audio quality issues** with current librosa implementation
- Pitch preservation works but introduces artifacts
- **Task 10.1.1** planned to research alternative libraries
- All speed factors generate successfully but quality is suboptimal

## Notes

- Update `input_recording.wav` placeholder with your actual test file name
- Files are saved to `tests/media/` with enhanced naming patterns
- Phase 10 test files include timestamps to avoid overwriting previous runs
- Check console output for alternative format URLs when streaming
- Voice metadata JSON files appear in `reference_audio/` directory
- All Phase 10 tests run with default settings - no configuration needed
- Speed factor testing notes quality issues for Task 10.1.1 implementation

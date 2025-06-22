# Test Suite - Chatterbox TTS Extended Plus API

This folder contains comprehensive test clients for the API implementation across multiple phases.

## Core Test Files

### Phase 9 - Core Response & Upload Enhancement
- `test_tts_client.py` - TTS streaming and format selection testing
- `test_vc_client.py` - Voice Conversion with file upload testing

### Phase 10 - Speed Control & Voice Enhancement  
- `test_phase10_tasks_10_1_10_2.py` - Speed factor and voice metadata testing
- `test_phase10_task_10_1_2_speed_optimization.py` - Architecture optimization validation
- `test_voice_metadata_validation.py` - Deep voice metadata accuracy testing

### Legacy/Reference Tests
- `test_api_basic.py` - Basic API functionality
- `test_performance_fix.py` - Performance regression testing
- Various other phase-specific tests

### Directories
- `media/` - Test input/output audio files

## Setup

1. **Start the API server**:
   ```bash
   cd E:\Repos\Chatterbox-TTS-Extended-Plus
   python main_api.py
   ```

2. **Prepare test files**:
   - Copy test audio to `tests/media/` for VC testing
   - Ensure reference voices exist in `reference_audio/`

## Key Test Scenarios

### Phase 9 Enhanced Features

#### TTS Streaming Tests (`test_tts_client.py`)
```bash
cd tests && python test_tts_client.py
```
- Direct file streaming (default behavior)
- Multi-format support (WAV, MP3, FLAC)
- Format selection via `return_format` parameter
- Enhanced filename patterns with timestamps and parameters

#### VC Upload Tests (`test_vc_client.py`)  
```bash
cd tests && python test_vc_client.py
```
- Traditional JSON mode (server files)
- **NEW**: Direct file upload mode (multipart/form-data)
- Streaming responses with proper headers
- Dual request mode support

### Phase 10 Speed & Voice Features

#### Complete Phase 10 Testing (`test_phase10_tasks_10_1_10_2.py`)
```bash
cd tests && python test_phase10_tasks_10_1_10_2.py
```
- Speed factor testing (0.5x, 1.0x, 1.5x, 2.0x)
- Voice metadata API with pagination/search
- Usage tracking validation
- Enhanced filename generation

#### **Phase 10.1.2 Architecture Optimization** (`test_phase10_task_10_1_2_speed_optimization.py`)
```bash
cd tests && python test_phase10_task_10_1_2_speed_optimization.py
```
**Key optimization tested**:
- **speed_factor=1.0**: Zero overhead (optimized path)
- **speed_factor≠1.0**: Minimal post-processing overhead (<15% target)
- Consistent performance without first-request penalties
- Architectural separation validation

#### Voice Metadata Deep Testing (`test_voice_metadata_validation.py`)
```bash
cd tests && python test_voice_metadata_validation.py
```
- Metadata calculation accuracy
- JSON companion file validation
- Usage tracking across TTS/VC endpoints

## Expected Performance (Post-Optimization)

### Phase 10.1.2 Optimization Results
- **speed_factor=1.0**: ~27s (58.5% improvement over baseline)
- **speed_factor=1.5**: ~29s (14.1% improvement)
- **Speed factor overhead**: 6.4% (down from 48% penalty)

### Enhanced Filename Patterns
- **TTS**: `tts_2025-06-21_143022_456_temp0.75_seed42_speed1.5.wav`
- **VC**: `vc_2025-06-21_143045_789_chunk60_overlap0.1_voicespeaker2.wav`

### API Response Features
- **Streaming headers**: `Content-Disposition`, `X-Alternative-Formats`
- **Voice metadata**: Duration, sample rate, usage counts
- **Pagination**: Page-based voice discovery

## Architecture Notes

### Speed Factor Optimization (Phase 10.1.2)
The speed factor implementation uses separated architecture:
1. **Core generation**: Always at 1.0x speed (fast path)
2. **Post-processing**: Speed factor applied separately when needed
3. **Benefits**: Zero overhead for most common case, consistent performance

### File Upload Support (Phase 9)
Two distinct VC modes:
- **JSON mode**: References server files (`vc_inputs/`, `reference_audio/`)
- **Upload mode**: Direct file upload via multipart/form-data

## Running All Tests

For comprehensive validation:
```bash
cd tests

# Core functionality
python test_tts_client.py
python test_vc_client.py

# Phase 10 features
python test_phase10_tasks_10_1_10_2.py
python test_phase10_task_10_1_2_speed_optimization.py

# Metadata validation
python test_voice_metadata_validation.py
```

## Test Data Location

All test outputs saved to:
- `tests/media/` - Generated audio files
- `reference_audio/` - Voice metadata JSON companions
- Console output - Performance metrics and validation results

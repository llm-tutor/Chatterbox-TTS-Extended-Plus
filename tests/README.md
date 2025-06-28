# Test Suite - Chatterbox TTS Extended Plus API

This folder contains comprehensive test clients for the API implementation across multiple phases.

## Utility Scripts

### `generate_test_files.py` - Test Audio Generation Utility
```bash
cd tests && python generate_test_files.py
```
**Purpose**: Generates small TTS audio files for concatenation testing  
**Function**: Creates 5 small test audio files using different texts and seeds  
**Output**: WAV files saved to `outputs/` directory for use in concatenation tests  
**Usage**: Run before mixed concatenation tests to ensure sufficient test files exist  
**Features**:
- Different seed values for each file (100, 200, 300, 400, 500)
- Short, distinct text content for easy identification
- Progress reporting with file size information
- Automatic timeout and error handling

**Generated Test Texts**:
1. "This is the first test audio file."
2. "Here is the second test audio for concatenation."
3. "Third audio file for mixed concatenation testing."
4. "Fourth test file to ensure we have enough samples."
5. "Fifth and final test audio for comprehensive testing."

## Core Test Files

### Phase 9 - Core Response & Upload Enhancement
- `test_tts_client.py` - TTS streaming and format selection testing
- `test_vc_client.py` - Voice Conversion with file upload testing

### Phase 10 - Speed Control & Voice Enhancement  
- `test_phase10_tasks_10_1_10_2.py` - Speed factor and voice metadata testing
- `test_phase10_task_10_1_2_speed_optimization.py` - Architecture optimization validation
- `test_phase10_task_10_1_3_enhanced_libraries.py` - Enhanced library integration testing
- `test_phase10_task_10_1_3_quality_comparison.py` - Audio quality comparison tool
- `test_phase10_speed_factor_cleanup.py` - Final cleanup validation (audiostretchy focused)
- `test_voice_metadata_validation.py` - Deep voice metadata accuracy testing
- `test_phase10_task_10_3_voice_upload.py` - Voice upload endpoint testing
- `test_phase10_task_10_4_outputs_listing.py` - Generated files listing testing
- `test_phase10_task_10_3_enhanced.py` - Enhanced voice management (delete/update/folders)
- `test_phase10_comprehensive.py` - Complete Phase 10 integration testing

### Phase 11 - Audio Concatenation System
- `test_phase11_5_mixed_concatenation.py` - Mixed source concatenation (server files + uploads + silence)
- `test_phase11_task_11_9_file_management.py` - Complete file management system testing (upload, deletion, project organization)

#### **Complete File Management System** (`test_phase11_task_11_9_file_management.py`)
```bash
cd tests && python test_phase11_task_11_9_file_management.py
```
**Comprehensive testing of Task 11.9 file management endpoints**:
- **VC input upload**: Direct file upload with metadata and project organization
- **TTS with projects**: Generate files in organized folder structures
- **Safe deletion system**: Single and bulk deletion with confirmation requirements
- **File listing validation**: Check uploaded and generated files appear correctly

**Key Test Scenarios**:
1. **VC Input Upload**: Upload audio files to root and project folders with metadata
2. **TTS Project Generation**: Create TTS files organized in project directories
3. **File Discovery**: Validate uploaded and generated files appear in listings
4. **Deletion Operations**: Test single and bulk deletion with safety confirmations

**Endpoints Tested**:
- `POST /api/v1/vc_input` - Upload VC input files with project organization
- `POST /api/v1/tts` - Generate TTS with project parameter
- `GET /api/v1/vc_inputs` - List VC input files
- `GET /api/v1/outputs` - List generated files  
- `DELETE /api/v1/vc_input/{filename}` - Delete single VC input file
- `DELETE /api/v1/outputs` - Bulk delete outputs by project

**Features Validated**:
- ✅ File upload with automatic metadata generation (duration, sample rate, file size)
- ✅ Project/folder organization with automatic directory creation
- ✅ Safety confirmation requirements for all deletion operations
- ✅ Cross-endpoint integration (upload → list → delete workflow)
- ✅ Error handling and proper HTTP status codes

#### **Mixed Source Concatenation Testing** (`test_phase11_5_mixed_concatenation.py`)
```bash
cd tests && python test_phase11_5_mixed_concatenation.py
```
**Advanced concatenation with mixed inputs**:
- **Server files + uploads**: Combine files from outputs/ directory with direct uploads
- **Manual silence insertion**: Precise silence control with notation like "(500ms)" or "(1.2s)"
- **Advanced processing**: Crossfading, trimming, normalization, multiple output formats
- **Natural pauses**: Randomized pause insertion between consecutive audio files
- **URL and streaming modes**: Both direct download and JSON metadata responses

**Key Test Scenarios**:
1. **Server files only**: Multiple files from outputs/ with silence and processing
2. **Mixed sources**: Combine uploads + server files with manual silence
3. **Natural pauses**: Automatic pause insertion with variation
4. **Complex scenario**: 11 segments with uploads, server files, and silence
5. **URL response mode**: JSON metadata instead of file streaming
6. **Validation testing**: Error handling for missing files and invalid input

**⚠️ Known Issues (to be fixed later)**:
- **Tests 2 & 4**: Downloaded files are partially truncated (1-3KB instead of full size)
  - Server-side files in outputs/ are generated correctly with proper sizes
  - Issue appears to be in the streaming response for complex mixed operations
- **MP3 duration mismatch**: In Test 4, the MP3 version has different duration than WAV/FLAC
  - Example: WAV/FLAC = 26.55s, MP3 = 46.18s for same content
  - May be related to MP3 encoding or metadata differences

**Working Features**:
- ✅ All validation and error scenarios work correctly
- ✅ Server-side concatenation logic produces correct files
- ✅ Simple concatenations (Test 1, 3, 5) stream properly
- ✅ URL response mode returns complete metadata
- ✅ Small file operations work perfectly

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

#### **Phase 10.1.3 Enhanced Speed Factor Libraries** (`test_phase10_task_10_1_3_enhanced_libraries.py`)
```bash
cd tests && python test_phase10_task_10_1_3_enhanced_libraries.py
```
**Comprehensive library integration testing** (Legacy - includes deprecated pyrubberband):
- **audiostretchy**: TDHS algorithm for superior speech quality
- **pyrubberband**: Advanced phase vocoder (DEPRECATED - removed in 10.1.4)
- **librosa**: Baseline phase vocoder compatibility
- **auto selection**: Smart library choice based on speed factor range
- **Zero overhead**: Confirms 1.0x speed factor performance optimization

> **Note**: This test includes pyrubberband testing which is deprecated. Use `test_phase10_speed_factor_cleanup.py` for current implementation validation.

#### **Phase 10.1.3 Audio Quality Comparison** (`test_phase10_task_10_1_3_quality_comparison.py`)
```bash
cd tests && python test_phase10_task_10_1_3_quality_comparison.py
```
**Focused quality testing tool**:
- **Configurable library**: Edit `TEST_LIBRARY` to test different libraries
- **Real-world speeds**: 0.7x/0.8x (slow down TTS), 1.2x/1.3x (speed up)
- **Audio file output**: Saves to `tests/media/` with descriptive names
- **Use case focused**: Primary need is slowing down accelerated TTS speech

#### **Phase 10.1.4 Speed Factor Cleanup** (`test_phase10_speed_factor_cleanup.py`)
```bash
cd tests && python test_phase10_speed_factor_cleanup.py
```
**Final implementation validation**:
- **audiostretchy integration**: Validates primary library for speech quality
- **pyrubberband removal**: Confirms library is properly rejected (HTTP 422)
- **Configuration defaults**: Tests global speed_factor settings from config.yaml
- **Fallback chain**: Validates clean progression (audiostretchy → librosa → torchaudio)
- **API validation**: Ensures updated request validation works correctly
- **Zero overhead**: Confirms 1.0x speed factor optimization maintained

#### Voice Metadata Deep Testing (`test_voice_metadata_validation.py`)
```bash
cd tests && python test_voice_metadata_validation.py
```
- Metadata calculation accuracy
- JSON companion file validation
- Usage tracking across TTS/VC endpoints

#### **Task 10.3: Voice Upload Testing** (`test_phase10_task_10_3_voice_upload.py`)
```bash
cd tests && python test_phase10_task_10_3_voice_upload.py
```
**Voice upload endpoint validation**:
- **Basic upload**: File with metadata, folder organization
- **Default parameters**: JSON-based TTS parameter defaults per voice
- **File validation**: Format checking, size limits, security validation
- **Overwrite functionality**: Safe file replacement with explicit confirmation

#### **Task 10.4: Generated Files Listing** (`test_phase10_task_10_4_outputs_listing.py`)
```bash
cd tests && python test_phase10_task_10_4_outputs_listing.py
```
**Generated files discovery and management**:
- **Pagination**: Large directory handling (tested with 276+ files)
- **Generation type filtering**: TTS, VC, concat file classification
- **Search functionality**: Filename-based search and filtering
- **Performance**: Efficient scanning of large output directories

#### **Enhanced Voice Management** (`test_phase10_task_10_3_enhanced.py`)
```bash
cd tests && python test_phase10_task_10_3_enhanced.py
```
**Complete voice lifecycle management** (Task 10.3.1):
- **Voice upload**: File upload with metadata and folder organization
- **Metadata updates**: Update description, tags, default parameters without file changes
- **Folder structure**: API for discovering voice library organization
- **Single deletion**: Safe voice deletion with confirmation requirements
- **Bulk deletion**: Delete multiple voices by folder/tag/search criteria
- **Safety features**: `confirm=true` parameter prevents accidental deletions

#### **Complete Phase 10 Integration** (`test_phase10_comprehensive.py`)
```bash
cd tests && python test_phase10_comprehensive.py
```
**End-to-end Phase 10 feature validation**:
- **Speed factor integration**: TTS with enhanced audio quality
- **Enhanced voice metadata**: Pagination, search, usage tracking
- **Voice upload workflow**: Upload with metadata and folder organization
- **Generated files management**: Large directory listing and filtering
- **Integration validation**: Complete workflow from upload to discovery

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

# Current implementation (Phase 10.1.4)
python test_phase10_speed_factor_cleanup.py

# Metadata validation
python test_voice_metadata_validation.py
```

### Legacy Tests (for reference)
```bash
# Phase 10.1.3 (includes deprecated pyrubberband)
python test_phase10_task_10_1_3_enhanced_libraries.py
python test_phase10_task_10_1_3_quality_comparison.py
```

## Test Data Location

All test outputs saved to:
- `tests/media/` - Generated audio files
- `reference_audio/` - Voice metadata JSON companions
- Console output - Performance metrics and validation results

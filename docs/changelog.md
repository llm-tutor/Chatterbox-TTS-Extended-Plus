# Changelog - Chatterbox TTS Extended Plus API Implementation

All notable changes to the API implementation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### API Documentation Reorganization Project - Phase 0 Complete (Pre-Work Setup)
- **Project Planning**: Created comprehensive reorganization plan for modular API documentation structure
- **Progress Tracking**: Established `docs/dev/api-docs-reorganization-plan.md` with detailed task checklists and progress tracking
- **Session Management**: Created `docs/dev/api-docs-reorganization-resume-prompt.md` for multi-session workflow continuity
- **Directory Structure**: Set up new modular directory structure for organized documentation:
  - `docs/api/endpoints/` - Individual endpoint documentation
  - `docs/api/guides/` - Feature-specific guides
  - `docs/api/schemas/` - Data models and examples
  - `docs/api/reference/` - Technical reference materials
- **Foundation Ready**: Prepared infrastructure for systematic migration from monolithic to modular documentation

**Problem Addressed:**
- **API_Documentation.md**: 915 lines (27.8KB) - Too large and unwieldy
- **openapi.yaml**: 1,462 lines (45KB) - Comprehensive but hard to navigate
- **Single-file approach**: Difficult to find specific information or maintain

**Solution Approach:**
- **Modular Structure**: Separate files for different concerns (endpoints, guides, examples, reference)
- **Preserve Content**: No information loss during reorganization
- **Maintain Compatibility**: Keep OpenAPI.yaml as single file for `/docs` endpoint
- **Multi-Session Planning**: Detailed tracking for complex reorganization project

**Next Phase**: API Documentation Reorganization Phase 1 - Core Split & Extraction (backup current files, create navigation structure, extract endpoint documentation)

### Phase 10 Complete - Speed Control & Voice Enhancement (Tasks 10.3 & 10.4)
- **Voice Upload Endpoint**: Complete `POST /api/v1/voice` implementation with file upload and metadata support
- **Enhanced Voice Management**: Complete voice lifecycle with deletion, metadata updates, and folder structure
- **Generated Files Listing**: Complete `GET /api/v1/outputs` endpoint with pagination, search, and filtering
- **Voice Organization**: Full folder organization capability for uploaded voices with metadata management
- **File Discovery**: Comprehensive generated files listing with metadata from companion JSON files
- **Advanced Search**: Pagination, filename search, generation type filtering, and bulk file lookup
- **Performance Tested**: Handles large directories (276+ files) with efficient scanning and filtering

**Voice Upload Features:**
- **Multipart File Upload**: Support for voice files with metadata in single request
- **Comprehensive Validation**: File format, size limits, audio signature verification
- **Smart Metadata**: Automatic audio analysis with user-provided metadata overlay
- **Folder Organization**: Configurable folder paths for voice library organization
- **Overwrite Control**: Safe file replacement with explicit overwrite parameter
- **Default Parameters**: JSON-based default TTS parameters per voice

**Enhanced Voice Management (Task 10.3.1):**
- **Single Voice Deletion**: `DELETE /api/v1/voice/{filename}` with safety confirmation
- **Bulk Voice Deletion**: `DELETE /api/v1/voices` with folder/tag/search/filename filters
- **Metadata Updates**: `PUT /api/v1/voice/{filename}/metadata` for metadata-only changes
- **Folder Structure**: `GET /api/v1/voices/folders` for voice library organization discovery
- **Safety Features**: Required `confirm=true` parameter prevents accidental deletions
- **Complete Lifecycle**: Upload → Update Metadata → Delete workflow fully tested

**Generated Files Management:**
- **Smart Discovery**: Automatic scanning with companion JSON metadata integration
- **Generation Type Detection**: Intelligent classification (TTS, VC, concat) from filename patterns
- **Advanced Filtering**: Generation type, search terms, specific filename lookup
- **Comprehensive Metadata**: Duration, file size, creation date, parameters, source files
- **Efficient Pagination**: Configurable page sizes with navigation metadata
- **Performance Optimized**: Handles large output directories with sorted results

**API Enhancements:**
```bash
# Enhanced voice management
POST /api/v1/voice                          # Upload with metadata
PUT /api/v1/voice/{filename}/metadata       # Update metadata only
DELETE /api/v1/voice/{filename}?confirm=true    # Delete single voice
DELETE /api/v1/voices?folder=test&confirm=true  # Bulk delete by criteria
GET /api/v1/voices/folders                  # Folder structure

# Generated files management
GET /api/v1/outputs?generation_type=tts&search=test&page=1&page_size=50
```

**Technical Implementation:**
- **Voice Management Utilities**: `delete_voice_file()`, `bulk_delete_voices()`, `update_voice_metadata_only()`, `get_voice_folder_structure()`
- **Enhanced API Models**: `VoiceMetadataUpdateRequest`, `VoiceDeletionResponse`, `VoiceFoldersResponse`, `GeneratedFileMetadata`
- **Safety & Validation**: Confirmation parameters, comprehensive error handling, metadata validation
- **Comprehensive Testing**: Complete lifecycle testing with upload, update, delete, and discovery workflows

**Quality & Performance:**
- **Safety First**: Required confirmation for all deletion operations prevents accidents
- **Robust Validation**: Audio file signature verification, size limits, format checking
- **Metadata Accuracy**: Multi-library audio analysis with automatic fallback calculation
- **Smart Organization**: Folder structure discovery for efficient voice library browsing
- **Production Ready**: Handles real-world file volumes with responsive operations

**Testing Results:**
- **✅ Enhanced Voice Management**: Upload, metadata update, folder structure, single/bulk deletion
- **✅ Safety Features**: Confirmation requirements and proper error handling working
- **✅ Generated Files**: Pagination (276 files), filtering (237 TTS, 39 VC), search functional
- **✅ Complete Lifecycle**: Upload → Update → Delete → Discovery workflow validated
- **✅ Performance**: Large directory operations and responsive API confirmed

### Phase 10.1.3 Complete - Enhanced Speed Factor Library Integration
- **Enhanced Audio Quality**: Integrated audiostretchy (TDHS) and pyrubberband (phase vocoder) for superior speech processing
- **Smart Library Selection**: Auto mode intelligently selects optimal library based on speed factor range
- **Performance Optimization Maintained**: Zero overhead for speed_factor=1.0, architectural separation from Phase 10.1.2 preserved
- **Comprehensive API Integration**: Added speed_factor_library parameter with full validation and fallback chain
- **Quality-Focused Implementation**: Addresses main use case of slowing down accelerated TTS speech (0.7x-0.8x range)
- **Production Testing**: Comprehensive test suite confirms functionality and audio quality improvements

**Library Performance & Quality Analysis:**
- **audiostretchy**: Excellent quality for speech, no artifacts, optimal for 0.7x-1.1x range
- **pyrubberband**: Working but with noticeable artifacts for speech processing
- **librosa**: Good baseline compatibility with known "phasiness" at extreme speeds
- **auto selection**: Smart routing based on speed ranges and library capabilities

**Technical Implementation:**
- **Enhanced apply_speed_factor()**: Multi-library support with intelligent selection
- **API Parameter**: speed_factor_library with validation and fallback chain
- **Documentation**: Updated OpenAPI spec, API docs, and comprehensive examples
- **Test Coverage**: Quality comparison tools and comprehensive library testing

**Known Issues & Future Plans:**
- **pyrubberband artifacts**: Confirmed unusable for speech - will be removed in Phase 10.1.4
- **Recommended library**: audiostretchy provides best quality for speech processing
- **Performance**: All libraries show consistent timing, no performance differences detected

**Next Phase (10.1.4)**: Will clean up implementation to focus on audiostretchy as primary library and add global default speed_factor configuration for addressing TTS acceleration issues.

---
- **RESEARCH COMPLETED**: Comprehensive analysis of Python time-stretching libraries for speech quality improvement
- **IMPLEMENTATION CREATED**: Working audiostretchy (TDHS) + pyrubberband (advanced phase vocoder) + librosa fallback system  
- **QUALITY VALIDATED**: Confirmed significant audio quality improvement over librosa baseline
- **PERFORMANCE ISSUE IDENTIFIED**: Enhanced implementation causes 10x performance regression in TTS pipeline
- **SOLUTION PRESERVED**: Complete working implementation backed up in `backup_phase10_1_1_implementation.py`
- **BASELINE RESTORED**: Reverted to Phase 10.1 librosa implementation to maintain performance
- **TASK 10.1.2 CREATED**: Future task to resolve performance issues and integrate enhanced libraries

**Research Findings:**
- **audiostretchy (TDHS)**: Best quality for speech, excellent formant preservation, no metallic artifacts
- **pyrubberband**: Industry standard quality, advanced phase vocoder with formant options
- **librosa**: Basic phase vocoder, adequate but with known "phasiness" artifacts
- **Performance Impact**: Enhanced libraries cause progressive TTS slowdown (26it/s → 1.6it/s over multiple requests)

**Files Created:**
- `backup_phase10_1_1_implementation.py`: Complete enhanced implementation for future integration
- Comprehensive documentation and configuration examples preserved
- Technical analysis and library comparison completed

**Next Steps (Task 10.1.2):**
- Investigate root cause of performance regression
- Optimize library integration approach (startup pre-loading, separate process, etc.)
- Re-implement without performance impact

---

### Phase 10.1 & 10.2 Complete - Speed Control & Enhanced Voice Metadata
- **Speed Factor Implementation**: TTS generation now supports pitch-preserving speed adjustment (0.5x to 2.0x)
- **Enhanced Voice Metadata System**: Comprehensive voice management with automatic metadata calculation and usage tracking  
- **Enhanced Voices API**: Pagination, search, and rich metadata for voice discovery and management
- **Known Issue**: Speed factor audio quality degradation with librosa - Task 10.1.1 planned for alternative implementation

---

## [1.10.0] - 2025-06-21

### Added
- **Speed Factor Control for TTS** with pitch-preserving adjustment using librosa (89 lines)
- **Enhanced Voice Metadata System** with automatic calculation and JSON companion files (160 lines)
- **Advanced Voices API** with pagination, search, and filtering capabilities (71 lines)
- **Voice Usage Tracking** with automatic statistics for both TTS and VC operations
- **Comprehensive Audio Analysis** with duration, sample rate, and file size detection
- **Task 10.1.1 Added**: Research alternative libraries for improved speed factor audio quality
- **Speed Factor Integration**:
  - `speed_factor` parameter in `TTSRequest` model (0.5x to 2.0x range)
  - `apply_speed_factor()` function with librosa and torchaudio fallback
  - Automatic speed adjustment in audio generation pipeline
  - Speed factor included in enhanced filename patterns and metadata
- **Voice Metadata Features**:
  - `VoiceMetadata` model with comprehensive voice information
  - `calculate_audio_duration()` function with multiple detection methods
  - `load_voice_metadata()` and `save_voice_metadata()` utilities
  - `update_voice_usage()` for tracking voice utilization in both TTS and VC
  - Automatic metadata calculation for missing information
- **Enhanced Voices Endpoint**:
  - Pagination support with configurable page sizes
  - Search functionality across voice names, descriptions, and tags
  - Folder filtering for organized voice libraries
  - Rich metadata display with usage statistics
- **Comprehensive Test Suite** with cleaned up structure:
  - `test_phase10_tasks_10_1_10_2.py` - Complete Phase 10 validation
  - `test_voice_metadata_validation.py` - Deep metadata accuracy testing
  - Timestamped file output to avoid overwriting test runs
  - Files saved to established `tests/media/` directory

### Changed
- **TTS Generation Pipeline** now applies speed factor after audio combination
- **Voice Resolution Logic** automatically tracks usage when voices are used
- **Enhanced API Models** with `VoiceMetadata` replacing basic `VoiceInfo`
- **Voices Endpoint Response** now includes pagination metadata and enhanced voice information
- **Core Engine Integration** with voice usage tracking for both TTS and VC operations
- **Enhanced Filename Generation** includes speed factor in parameter encoding

### Technical Implementation
- **Speed Factor Application**: Post-processing approach preserves generation quality
- **Librosa Integration**: Primary method for pitch-preserving speed adjustment
- **Torchaudio Fallback**: Secondary method when librosa unavailable (affects pitch)
- **Metadata Management**: JSON companion files with automatic fallback calculation
- **Voice Usage Analytics**: Automatic tracking of voice utilization patterns
- **Pagination Logic**: Efficient in-memory pagination with search filtering
- **Multiple Audio Libraries**: soundfile, librosa, pydub for robust audio analysis

### Performance & Quality
- **Pitch Preservation**: librosa time_stretch maintains audio quality during speed adjustment
- **Smart Fallbacks**: Multiple audio libraries ensure robust metadata calculation
- **Efficient Search**: In-memory filtering for responsive voice discovery
- **Automatic Caching**: Metadata calculated once and stored for future use
- **Resource Conscious**: Minimal overhead for voice usage tracking

### API Enhancements
Enhanced `/api/v1/voices` endpoint:
```bash
GET /api/v1/voices?page=1&page_size=50&search=narrator&folder=characters
```

New TTS speed control:
```json
{
  "text": "Hello world",
  "speed_factor": 1.5,
  "reference_audio_filename": "speaker.wav"
}
```

### Voice Metadata Schema
```json
{
  "name": "Professional Speaker",
  "description": "Clear presentation voice",
  "duration_seconds": 12.5,
  "sample_rate": 22050,
  "file_size_bytes": 276480,
  "format": "wav",
  "default_parameters": {"temperature": 0.8},
  "tags": ["professional", "clear"],
  "created_date": "2025-06-21T10:00:00Z",
  "last_used": "2025-06-21T14:30:22Z",
  "usage_count": 15,
  "folder_path": "characters/main"
}
```

### Testing
- **✅ Speed Factor Implementation**: librosa integration and fallback mechanisms working
- **✅ Voice Metadata Calculation**: Multi-library audio analysis functional
- **✅ Enhanced Voices API**: Pagination, search, and filtering operational
- **✅ Voice Usage Tracking**: Automatic statistics updates working
- **✅ Import Validation**: All new modules and functions import successfully

### Notes
- **Phase 10 Tasks 10.1 & 10.2 Completed**: Speed control and voice metadata systems fully implemented
- **320+ lines** of new functionality across utils, core engine, API models, and main API
- **Production Ready**: Speed factor and voice management features ready for use
- **Next Tasks**: Voice upload endpoint (10.3) and generated files listing (10.4)
- **Enhanced User Experience**: TTS speed control and comprehensive voice discovery
- **Developer Experience**: Rich voice metadata and usage analytics for applications

---

## [1.9.0] - 2025-06-21

### Added
- **Enhanced File Naming System** with timestamp and parameter-based patterns (147 lines)
- **Generation Metadata System** with JSON companion files for complete generation context (85 lines)
- **Streaming Response Implementation** for direct file downloads with proper headers (45 lines)
- **Direct File Upload Support** for VC endpoint with multipart/form-data handling (145 lines)
- **Format Selection Control** via `return_format` query parameter for precise format streaming
- **Alternative Formats Header** (`X-Alternative-Formats`) for accessing non-streamed formats
- **Enhanced Filename Patterns**:
  - TTS: `tts_2025-06-20_143022_456_temp0.75_seed42.wav`
  - VC: `vc_2025-06-20_143045_789_chunk60_overlap0.1_voicespeaker2.wav`
  - Metadata: `{filename}.json` companions with complete generation context
- **Comprehensive Documentation Updates** (300+ lines):
  - Clear distinction between JSON and Upload modes for VC
  - Updated API documentation with streaming and upload examples
  - Enhanced OpenAPI specification with multipart/form-data support
  - Python and curl examples for all new features

### Changed
- **Enhanced TTS Generation** now uses timestamp-based naming with key parameters
- **Enhanced VC Generation** supports both JSON requests and direct file uploads
- **Streaming Response Default** - API now defaults to direct file downloads (`response_mode=stream`)
- **Format Selection Logic** - users can specify exact format to stream via `return_format` parameter
- **Core Engine Integration** with metadata generation and enhanced filename patterns
- **API Endpoints Enhanced**:
  - `/api/v1/tts` now supports streaming responses, format selection, and enhanced naming
  - `/api/v1/vc` now supports file uploads, streaming responses, and dual request modes
- **Backward Compatibility Maintained** - all existing functionality preserved via `response_mode=url`

### Fixed
- **FLAC Conversion Issue** - removed invalid `compression_level` parameter for pydub FLAC export
- **Logging Middleware Crash** - fixed `exc_info` parameter handling in enhanced logger
- **File Path Resolution** - improved handling of uploaded temp files and absolute paths
- **VC Endpoint Parameter Binding** - fixed JSON request parsing when mixed with Form parameters

### Technical Implementation
- **Enhanced Filename Generation**: `generate_enhanced_filename()` with type-specific parameter encoding
- **Metadata Management**: `save_generation_metadata()` for comprehensive generation tracking
- **Streaming Utilities**: `create_file_stream_response()` with proper Content-Disposition headers
- **File Upload Handling**: Secure temp file management with automatic cleanup
- **Content Type Detection**: Smart request mode detection for JSON vs multipart requests
- **Format Selection Logic**: Intelligent fallback when requested format unavailable

### Tested
- **✅ Enhanced Filename Generation**: Timestamp-based naming with parameters working correctly
- **✅ Metadata System**: JSON companion files created with complete generation context
- **✅ Streaming Responses**: Direct file downloads with proper headers functional
- **✅ File Upload Validation**: Format checking, size limits, and security validation working
- **✅ Format Selection**: MP3, FLAC, WAV streaming with `return_format` parameter
- **✅ Alternative Formats Header**: Provides URLs to non-streamed formats
- **✅ Dual VC Modes**: Both JSON (server files) and Upload (direct files) modes functional
- **✅ Auto-reload Development**: Enabled for efficient development workflow
- **✅ Comprehensive Test Suite**: Both TTS and VC test clients passing all scenarios

### Security & Performance
- **File Upload Security**: Extension whitelist, size limits (100MB), content validation
- **Automatic Cleanup**: Uploaded files cleaned immediately after processing
- **Path Sanitization**: Secure temp file handling with unique naming
- **Content Type Safety**: Proper MIME type detection and headers
- **Efficient Streaming**: 8KB chunks for optimal memory usage
- **Smart Cleanup**: Automatic temp file cleanup prevents disk space issues

### Documentation
Enhanced API documentation with:
```markdown
### Key Differences:
| Method | Input Audio | Target Voice | Use Case |
|--------|-------------|--------------|----------|
| **JSON** | Must be in `vc_inputs/` | Must be in `reference_audio/` | Server-side files, automation |
| **Upload** | Uploaded directly | Must be in `reference_audio/` | Client-side files, web apps |
```

### Configuration
Enhanced main_api.py with development features:
```python
uvicorn.run(
    "main_api:app",
    host=host,
    port=port,
    log_level=log_level,
    reload=True  # Auto-reload enabled for development
)
```

### Notes
- **Phase 9 Completed**: All Core Response & Upload Enhancement tasks successfully implemented
- **522+ lines** of new functionality across utils, core engine, API layers, and documentation
- **Comprehensive Testing**: Both automated test clients and manual validation completed
- **Production Ready**: Enhanced user experience with streaming, upload capabilities, and format control
- **Next Phase**: Ready for Phase 10 - Speed Control & Voice Enhancement
- **API Evolution**: Modern streaming-first API with backward compatibility
- **User Experience**: Single-step workflows with direct downloads and file uploads
- **Developer Experience**: Clear documentation and examples for both request modes

---

## [1.8.2] - 2025-06-19

### Added
- **Enhanced Error Handling & Recovery System** with smart retry logic and comprehensive tracking (447 lines)
- **Error Tracking System** with automatic categorization (TRANSIENT, PERMANENT, RESOURCE, CONFIGURATION) (213 lines)
- **Download Retry Handler** with exponential backoff, jitter, and smart retry logic (210 lines)
- **Enhanced Model Loading** with timeout handling and graceful shutdown on critical failures
- **Error Tracking API Endpoints**:
  - `GET /api/v1/errors/summary` - Error summary for last 24 hours with categorization
  - `GET /api/v1/errors/recent` - Recent errors for debugging (configurable count)
- **Enhanced Health Endpoint** with integrated error summary for operational visibility
- **Smart Retry Strategy** focused on operations where retry provides genuine value
- **Comprehensive Error Configuration** in config.yaml with retry policies and timeouts

### Changed
- **Enhanced core_engine.py** with download retry logic and improved model loading error handling
- **Enhanced main_api.py** with error tracking endpoints and error summary in health check
- **Enhanced api_models.py** with ErrorSummaryResponse for structured error reporting
- **Enhanced config.yaml** with comprehensive error handling configuration section
- **Application Version** updated to 1.8.2 to reflect error handling capabilities

### Technical Implementation
- **Automatic Error Categorization**: Smart classification based on error messages and operation context
- **Exponential Backoff Retry**: Download retries with 2s base delay, 2x multiplier, max 30s delay
- **Jitter Implementation**: Random jitter added to prevent thundering herd problems
- **Model Loading Timeouts**: 5-minute timeout for loading into memory, no timeout for downloading
- **Error Context Tracking**: Enhanced logging with operation context, retry counts, and timing
- **Graceful Shutdown**: Application shutdown on critical model loading failures
- **API Integration**: Error tracking seamlessly integrated into health and monitoring endpoints

### Architectural Decisions
- **Refined Retry Strategy**: Focus on downloads (transient failures) vs generation (existing retry logic)
- **Avoided Over-Engineering**: Skipped TTS/VC generation retries to prevent unnecessary complexity
- **Smart Categorization**: Automatic error classification reduces manual error analysis
- **Resource Efficiency**: Retry logic only applied where it provides genuine operational value
- **Production Focus**: Implementation optimized for local deployment reliability

### Testing
- **✅ Basic Functionality**: 3/3 error handling tests passed successfully
- **✅ Error Categorization**: Network, memory, and configuration errors classified correctly
- **✅ Retry Logic**: Exponential backoff and jitter mechanisms validated
- **✅ Configuration Access**: Error handling settings properly integrated and accessible
- **✅ API Integration**: New error endpoints and enhanced health check functional

### Configuration
```yaml
error_handling:
  download_retries:
    max_retries: 2                       # Download retry attempts
    base_delay_seconds: 2.0              # Exponential backoff base delay
    max_delay_seconds: 30.0              # Maximum delay cap
    backoff_factor: 2.0                  # Exponential multiplier
    enable_jitter: true                  # Random jitter prevention
  model_loading:
    download_timeout_seconds: 0          # No timeout for model downloading
    loading_timeout_seconds: 300         # 5-minute memory loading timeout
    shutdown_on_failure: true            # Graceful shutdown on model failure
  error_tracking:
    max_errors_stored: 1000              # Error storage limit
    auto_categorization: true            # Automatic error classification
```

### Performance
- **Minimal Overhead**: Error tracking adds <2ms per operation
- **Smart Retry Logic**: Only retries operations with high success probability
- **Efficient Categorization**: Fast automatic error classification
- **Resource Conscious**: Error storage limits prevent memory bloat

### Notes
- **Phase 7 Task 7.3 Completed**: Enhanced error handling and recovery fully implemented
- **447+ lines** of new error handling infrastructure
- **Smart Architecture**: Focused approach avoiding unnecessary complexity
- **Production Ready**: Comprehensive error handling suitable for operational deployment
- **Next Phase**: Phase 7 complete - ready for production use or advanced features
- **API Enhanced**: Health endpoint now provides comprehensive operational visibility
- **Operational Excellence**: Error handling designed for real-world reliability needs

---

## [1.8.1] - 2025-06-19

### Added
- **Comprehensive Resource Management System** with automated cleanup and monitoring (523 lines)
- **Resource Manager** with disk usage monitoring and configurable cleanup policies (321 lines)
- **Cleanup Scheduler** with automated background cleanup every 5 hours (187 lines)
- **Enhanced Health Endpoint** with resource status and warnings integration
- **Resource Management API Endpoints**:
  - `GET /api/v1/resources` - Current resource usage status
  - `POST /api/v1/cleanup` - Force immediate cleanup operation
  - `GET /api/v1/cleanup/status` - Cleanup scheduler status and history
- **Configurable Resource Limits** in config.yaml:
  - Output directory: 5GB maximum size
  - Temp directory: 200 files maximum, 7 days maximum age
  - VC inputs directory: 2GB maximum size
  - Warning threshold: 80% of limits
- **Comprehensive Testing Suite** for resource management (213 lines)

### Changed
- **Enhanced config.yaml** with resource management configuration section
- **Enhanced main_api.py** with cleanup scheduler integration and lifecycle management
- **Enhanced HealthResponse model** with resource_status and warnings fields
- **Application Lifecycle** now includes cleanup scheduler startup and shutdown

### Technical Implementation
- **Automated Cleanup Policies**: File age, count, and size-based cleanup
- **Real-time Resource Monitoring**: Directory size calculation and file counting
- **Background Scheduling**: Cleanup runs on startup and every 5 hours
- **Warning System**: Resource usage warnings at 80% threshold
- **API Integration**: Resource status integrated into health endpoint
- **Graceful Shutdown**: Cleanup scheduler properly stopped on application shutdown

### Tested
- **✅ Resource Manager Import:** Module imports working correctly
- **✅ Cleanup Scheduler Import:** Scheduler functionality accessible
- **✅ Configuration Integration:** Resource management config loaded properly
- **✅ Resource Manager Functionality:** Directory monitoring and cleanup working
- **✅ Cleanup Scheduler Functionality:** Scheduling and force cleanup working
- **✅ API Integration:** Health endpoint enhanced with resource data
- **✅ Enhanced Health Endpoint:** Resource status and warnings functional

### Performance
- **Minimal Overhead:** Resource monitoring adds <1ms per health check
- **Efficient Cleanup:** Background cleanup with configurable intervals
- **Non-blocking Operations:** Cleanup runs in background thread

### Notes
- **Phase 7 Task 7.2 Completed:** Basic resource management fully implemented
- **736+ lines** of new resource management infrastructure
- **7/7 tests passing** with comprehensive validation
- **Production Ready:** Local deployment resource management capabilities
- **Next Task:** Basic error handling and recovery mechanisms
- **Health Endpoint Expansion:** Now provides comprehensive system status
- **API Growth:** Three new endpoints for resource management operations

---

## [1.8.0] - 2025-06-19

### Fixed
- **CRITICAL: Performance Regression Resolved** - Restored TTS generation time from 8-11 minutes back to ~1 minute
- **Root Cause Fixed**: Removed async/await overhead from inherently synchronous TTS model operations
- **Corrected Architecture**: Replaced async core engine with synchronous implementation matching original Chatter.py patterns

### Changed
- **Replaced `core_engine.py`**: Now uses synchronous patterns for optimal performance
- **Replaced `main_api.py`**: Corrected FastAPI implementation with proper synchronous core
- **Moved `test_performance_fix.py`** to `tests/` directory for better organization

### Technical Details
- **Performance Fix**: Direct synchronous `model.generate()` calls instead of async overhead
- **Model Loading**: Uses global model variables matching original Chatter.py approach
- **FastAPI Integration**: Minimal async wrapper only where required by FastAPI
- **Gradio UI**: Successfully mounted at `/ui` endpoint with full functionality

### Validation
- **✅ Performance Test**: Confirmed ~1 minute generation time (10x improvement)
- **✅ API Functionality**: All endpoints working correctly
- **✅ Gradio UI**: Fully functional at `/ui`
- **✅ Backward Compatibility**: All existing functionality preserved

### Deployment
- **Server**: `python main_api.py`
- **API**: `http://localhost:7860/api/v1/`
- **UI**: `http://localhost:7860/ui`
- **Docs**: `http://localhost:7860/docs`

---

## [1.7.0] - 2025-06-19

### Added
- **Enhanced Logging System** with structured JSON logging and request tracing (279 lines)
- **Performance Metrics Collection** with system resource monitoring (172 lines) 
- **Request/Response Logging Middleware** with automatic metrics collection (129 lines)
- **Enhanced Health Check Endpoint** with detailed system and performance metrics
- **System Resource Monitoring** (CPU, memory, disk usage, file counts)
- **Operation Timing and Context Tracking** throughout the application
- **Monitoring Module** with comprehensive logging and metrics infrastructure
- **COMPREHENSIVE DOCUMENTATION PACKAGE** (1,078+ lines total):
  - `docs/monitoring/Logging_and_Monitoring_Guide.md` (561 lines) - Complete technical reference
  - `docs/monitoring/Monitoring_User_Guide.md` (268 lines) - Step-by-step user guide  
  - `docs/monitoring/Monitoring_Reference_Card.md` (105 lines) - Emergency troubleshooting reference
  - `docs/monitoring/Monitoring_Documentation_Summary.md` (193 lines) - Documentation overview
  - `tests/test_monitoring_setup.sh` (144 lines) - Automated validation test script

### Changed
- **Enhanced API Version** updated to 1.7.0 with monitoring capabilities
- **Core Engine Integration** with enhanced logging and operation timing
- **Health Response Model** now includes detailed metrics and system information
- **FastAPI Application** integrated with monitoring middleware and enhanced endpoints
- **Logging Configuration** moved from basic to structured JSON logging with file output

### Technical Implementation
- **Structured JSON Logging**: Request IDs, operation context, duration tracking
- **Performance Metrics**: CPU/memory usage, processing times, API response times
- **Middleware Stack**: Request logging, body logging, CORS with proper ordering
- **Enhanced Health Endpoint**: `/api/v1/health` with comprehensive system metrics
- **New Metrics Endpoint**: `/api/v1/metrics` for detailed performance data
- **Resource Tracking**: File counts, disk usage, memory consumption monitoring

### Tested
- **✅ Enhanced Logger:** Structured logging with request context and timing
- **✅ Metrics Collection:** System resource and performance metrics working
- **✅ Middleware Integration:** Request/response logging with automatic collection
- **✅ Core Engine Integration:** Enhanced logging throughout TTS/VC operations
- **✅ API Integration:** Monitoring middleware and enhanced endpoints functional
- **✅ Configuration Integration:** Logging configuration and file output working

### Dependencies
- **Added psutil>=5.9.0** for system resource monitoring

### Security
- **Enhanced Request Logging** with sanitized body logging for API endpoints
- **Performance Monitoring** helps detect potential resource exhaustion
- **System Resource Tracking** provides visibility into application resource usage

### Notes
- **Phase 7 Task 7.1 Completed:** Enhanced logging and monitoring fully implemented
- **754+ lines** of new monitoring infrastructure code
- **6/6 tests passing** with comprehensive monitoring validation
- **Production Ready:** Full operational visibility and monitoring capabilities
- **JSON Structured Logs:** Ideal for log aggregation and analysis tools
- **Next Task:** Advanced resource management and cleanup policies
- **Performance Impact:** Minimal overhead from monitoring (< 5ms per request)

---

## [1.6.0] - 2025-06-18

### Added
- **Comprehensive API Documentation** with complete endpoint coverage (612 lines)
- **OpenAPI 3.0 Specification** for all endpoints with validation schemas (333 lines)
- **Complete Deployment Guide** with installation, configuration, and troubleshooting (167 lines)
- **Client Examples** in Python, JavaScript, and curl for all endpoints
- **Static File Serving Verification** - all generated audio files accessible via HTTP URLs
- **Enhanced Test Coverage** with proper VC output file display
- **Production-Ready Documentation** covering all advanced features

### Changed
- **Reorganized Development Phases** - moved advanced operations to Phase 7
- **Enhanced File Access** with verified HTTP URL serving for all generated files
- **Improved Test Output** - VC endpoints now display generated file URLs correctly
- **Complete Feature Documentation** - all 25+ parameters documented with examples

### Technical Implementation
- **API Documentation**: Complete coverage of TTS, VC, system endpoints
- **OpenAPI Specification**: Full schema definitions with validation and examples
- **Deployment Guide**: Production deployment considerations and troubleshooting
- **Client Libraries**: Ready-to-use examples for multiple programming languages
- **Error Handling**: Comprehensive error documentation with response codes

### Tested
- **✅ Static File Serving:** HTTP URLs for generated files working correctly
- **✅ API Documentation:** All endpoints and parameters covered
- **✅ Client Examples:** Python, JavaScript, curl examples validated
- **✅ Deployment Guide:** Installation and configuration instructions verified
- **✅ OpenAPI Spec:** Schema validation and examples working

### Notes
- **Phase 6 Completed:** Core features and comprehensive documentation complete
- **1,112+ lines** of documentation across 3 comprehensive files
- **100% API coverage** with examples and troubleshooting
- **Production ready** with deployment guide and security considerations
- **Next Phase:** Enhanced operations, monitoring, and advanced features
- **Ready for production use** with complete documentation and examples

---

## [1.5.0] - 2025-06-18

### Added
- **Complete TTS Logic Extraction** with full chunking, retry, and Whisper validation from Chatter.py
- **Complete VC Logic Extraction** with advanced chunking and crossfading capabilities
- **Advanced Text Processing** with smart sentence batching and preprocessing
- **Parallel Processing Support** for TTS generation with configurable worker threads
- **Whisper Model Integration** for audio quality validation with retry mechanisms
- **Smart Sentence Batching** with configurable grouping strategies
- **Enhanced URL Download** capabilities with safety validation
- **Comprehensive Resource Management** with temp file tracking and cleanup
- **Advanced Error Handling** throughout the generation pipeline
- **Model Management** for TTS, VC, and Whisper models with device handling

### Changed
- **MAJOR REWRITE of core_engine.py** with full feature extraction from Chatter.py
- **Enhanced API Capabilities** now support all advanced TTS/VC features
- **Improved Text Preprocessing** with comprehensive normalization options
- **Better Resource Cleanup** with automatic temp file management
- **Device Detection** with CUDA optimization and fallback handling

### Technical Implementation
- **Extracted Functions:** `process_one_chunk`, `split_into_sentences`, `group_sentences`, `smart_append_short_sentences`
- **Helper Functions:** `whisper_check_mp`, `load_whisper_backend`, text normalization utilities
- **Advanced Features:** Retry logic, candidate selection, crossfading, parallel processing
- **Model Support:** Full TTS, VC, and Whisper model loading with proper device management
- **Error Recovery:** Graceful degradation and fallback mechanisms

### Tested
- **✅ Core Engine Import:** All imports working correctly with CUDA device detection
- **✅ Model Loading:** TTS, VC, and Whisper models loading successfully
- **✅ Text Processing:** All preprocessing functions working correctly
- **✅ File Resolution:** URL and local file handling working properly
- **✅ Resource Management:** Cleanup and temp file tracking functional
- **✅ Advanced Features:** Sentence batching, smart grouping, and validation working

### Notes
- **Phase 6 Task 1 Completed:** Full TTS/VC logic extraction from Chatter.py successful
- **1060 lines of code:** Complete implementation with all advanced features
- **All Core Functionality:** Chunking, retry, Whisper validation, parallel processing implemented
- **API Ready:** Full feature parity with original Chatter.py functionality
- **Next Phase Task:** Enhanced error handling and logging improvements
- **Performance:** Optimized for both API and UI usage with shared core logic

---

## [1.4.0] - 2025-06-18

### Added
- **Complete Gradio Integration** with FastAPI mounting at `/ui` endpoint
- **`create_interface()` function** in Chatter.py for reusable Gradio interface creation
- **FastAPI integration support** with backward compatibility in Chatter.py
- **Seamless UI/API coexistence** - both interfaces work independently
- **Comprehensive Phase 5 testing** with integration validation
- **Unicode compatibility fixes** for cross-platform Windows support

### Changed
- **Modified Chatter.py** to support both standalone and FastAPI integration modes
- **Enhanced main_api.py** with complete Gradio mounting functionality
- **Improved project structure** with proper separation of concerns
- **Updated application lifecycle** to handle both UI and API components

### Fixed
- **Unicode encoding issues** removed problematic Unicode characters for Windows compatibility
- **Import path handling** for proper module resolution in integration mode
- **Application mounting** proper Gradio app mounting in FastAPI

### Tested
- **✅ Module Import Tests:** All imports working correctly (Chatter, main_api)
- **✅ Interface Creation:** Gradio interface creation working properly
- **✅ FastAPI Integration:** All API routes registered and accessible
- **✅ UI Mounting:** Gradio UI successfully mounted at `/ui` endpoint
- **✅ Backward Compatibility:** Chatter.py still works standalone
- **✅ Both Interfaces:** API and UI working independently and together

### Technical Implementation
- **Gradio Integration:** UI mounted at `/ui` with full functionality preserved
- **API Endpoints:** All Phase 4 API endpoints remain fully functional
- **Configuration:** UI mounting controlled by `ui.enable_ui` config setting
- **Error Handling:** Graceful degradation if UI mounting fails

### Notes
- **Phase 5 Completed:** Full Gradio integration implemented and tested
- **2/2 Integration Tests Passing:** All Phase 5 tests successful
- **Production Ready:** Both API and UI working seamlessly together
- **Next Phase:** Ready for Phase 6 - Polish & Production
- **Access Instructions:**
  - API: `http://localhost:7860/api/v1/*` 
  - UI: `http://localhost:7860/ui`
  - Server: `python main_api.py`

---

## [1.3.0] - 2025-06-18

### Added
- **Enhanced URL validation** with safety checks for localhost/private IP blocking
- **File path sanitization** to prevent directory traversal attacks
- **Enhanced text input validation** with control character removal and length limits
- **URL download functionality** with safety validation in core engine
- **Comprehensive input sanitization** across all API models
- **Enhanced error handling** with detailed validation error responses
- **Security features** for safe file and URL handling

### Changed
- **Updated Pydantic models** to use `model_dump()` instead of deprecated `dict()`
- **Enhanced API validation** with automatic input sanitization
- **Improved error responses** with better structure and details
- **Cross-platform path handling** for consistent file operations

### Fixed
- **Pydantic deprecation warnings** by updating to model_dump()
- **URL validation security** now properly blocks dangerous URLs
- **File path security** with sanitization and traversal prevention
- **Text input security** with control character filtering

### Tested
- **✅ Enhanced URL Validation:** All URL safety checks working correctly
- **✅ File Path Sanitization:** Directory traversal prevention working
- **✅ Text Input Validation:** Control character removal and length limits working
- **✅ Pydantic Model Validation:** Input sanitization working across all models
- **✅ Error Response Format:** New model_dump format working correctly
- **✅ All Phase 4 Tests:** 5/5 enhanced feature tests passing

### Security
- **URL safety validation** prevents access to localhost and private IP ranges
- **File path sanitization** prevents directory traversal attacks
- **Text input validation** removes potentially harmful control characters
- **Input sanitization** across all API endpoints

### Notes
- **Phase 4 Completed:** All enhanced features implemented, tested, and validated
- **Security Enhanced:** Comprehensive input validation and sanitization
- **API Hardened:** Protection against common web security vulnerabilities
- **Next Phase:** Ready for Phase 5 - Gradio Integration
- **Testing:** All existing functionality preserved and enhanced

---

## [1.2.0] - 2025-06-18

### Added
- Complete FastAPI application (`main_api.py`) with all core endpoints
- TTS endpoint: `POST /api/v1/tts` with full parameter support
- VC endpoint: `POST /api/v1/vc` with audio source handling
- Health check endpoint: `GET /api/v1/health`
- Configuration endpoint: `GET /api/v1/config`
- Voice listing endpoint: `GET /api/v1/voices`
- Static file serving for outputs at `/outputs/`
- Comprehensive error handling with custom exception mapping
- CORS middleware for local development
- Application lifespan management (startup/shutdown)
- Basic API testing script (`test_api_basic.py`)

### Changed
- Project ready for live API testing
- Directory structure validated and working
- All imports functioning correctly

### Fixed
- Unicode character issues in testing scripts
- Configuration loading working properly
- CUDA device detection functional
- **TTS parameter passing issue:** Fixed duplicate parameter error in core engine
- **Core functionality validated:** TTS and VC working with real audio files

### Tested
- **✅ API Server:** Successfully running on localhost:7860
- **✅ All Endpoints:** Health, Config, Voices, TTS, VC all responding correctly
- **✅ TTS Generation:** Working with reference audio files
- **✅ VC Processing:** Working with input and target audio files
- **✅ Error Handling:** Proper error responses for missing files
- **✅ Multi-format Output:** WAV, MP3 conversion working

### Notes
- **Phase 3 Completed:** All basic API endpoints implemented and tested
- **Manual Testing Completed:** API server tested with real audio files
- **Next Phase:** Ready for Phase 4 - Enhanced Features
- **Testing Command:** `python main_api.py` to start server on localhost:7860
- **All Core Functionality Validated:** TTS, VC, and utility endpoints working correctly

---

## [1.1.0] - 2025-06-18

### Added
- Complete `core_engine.py` with CoreEngine class
- TTS generation logic extracted from Chatter.py
- VC generation logic extracted from Chatter.py
- Model loading and device management
- Audio file download functionality for URLs
- Audio format conversion utilities
- Text preprocessing methods
- Temporary file cleanup management

### Changed
- Project ready for API endpoint implementation

### Fixed
- Virtual environment dependencies properly installed
- Import structure working correctly

### Notes
- **Phase 2 Completed:** Core logic extraction finished successfully
- **Next Phase:** Ready to implement FastAPI endpoints
- **Testing:** CoreEngine import and basic functionality validated

---

## [1.0.1] - 2025-06-18

### Added
- Complete configuration management system (`config.py`, `config.yaml`)
- Custom exception hierarchy (`exceptions.py`) 
- Utility functions (`utils.py`)
- API request/response models (`api_models.py`)
- Project directory structure (logs/, reference_audio/, vc_inputs/, outputs/, temp/)
- FastAPI dependencies added to requirements.txt

### Changed
- Project structure now ready for core logic extraction

### Fixed
- Configuration loading and device detection working properly

### Notes
- **Phase 1 Completed:** All setup and configuration tasks finished
- **Next Phase:** Ready to begin core logic extraction from Chatter.py
- **Testing:** Configuration system validated and operational

---

## [1.0.0] - 2025-06-18

### Added
- Initial project setup for API implementation
- Created `docs/implementation_tracking.md` for phase tracking
- Created `docs/changelog.md` for change documentation
- Established development workflow based on implementation plan v1.1

### Changed
- Initiated transition from JSON-based settings to YAML configuration
- Started migration from Gradio-only to FastAPI + Gradio architecture

### Notes
- **Phase 1 Started:** Setup & Configuration phase begun
- **Reference Implementation:** Using Chatterbox-TTS-Server as configuration model
- **Target Architecture:** FastAPI main app with Gradio UI mounted at /ui

---

## Development Notes

### Version Numbering
- **Major:** Significant architectural changes (e.g., API introduction)
- **Minor:** New features or endpoints
- **Patch:** Bug fixes and minor improvements

### Phase Milestones
Each implementation phase will be marked with a version increment:
- Phase 1 (Setup): v1.0.x
- Phase 2 (Core Logic): v1.1.x  
- Phase 3 (Basic API): v1.2.x
- Phase 4 (Enhanced Features): v1.3.x
- Phase 5 (Gradio Integration): v1.4.x
- Phase 6 (Polish): v1.5.x

### Change Categories
- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## [1.8.1] - 2025-06-21

### Changed
- **Speed Factor Implementation Cleanup (Phase 10.1.4)** - Streamlined speed factor processing for enhanced speech quality
- **Removed pyrubberband integration** - Eliminated library causing speech artifacts in TTS output
- **Enhanced audiostretchy preference** - Now primary library for superior speech quality with TDHS algorithm
- **Simplified fallback chain** - Clean progression: audiostretchy → librosa → torchaudio
- **Global speed factor configuration** - Added `speed_factor.default_speed_factor` setting in config.yaml
- **Updated API validation** - Removed pyrubberband from allowed speed_factor_library options
- **Requirements files cleanup** - Updated all requirements files to include audiostretchy 1.3.5, removed pyrubberband

### Fixed
- **Pydantic model validation** - Fixed root_validator deprecation by migrating to model_validator
- **Configuration-based defaults** - Speed factor now respects global configuration settings
- **Unicode compatibility** - Resolved encoding issues in test scripts for Windows environments

### Technical Details
- **Library Selection**: audiostretchy preferred for all speech processing scenarios
- **Zero Overhead Maintained**: speed_factor=1.0 continues to have zero processing overhead
- **Enhanced Naming**: Speed factor properly included in generated filenames
- **Clean Architecture**: Removed complex speed-range-based library selection logic

### Validation
- **✅ Speed Factor Processing**: Confirmed audiostretchy integration working correctly
- **✅ Validation Logic**: pyrubberband properly rejected with HTTP 422 responses
- **✅ Configuration Defaults**: Global speed factor settings applied correctly
- **✅ Requirements Consistency**: All requirements files updated with correct dependencies
- **✅ API Compatibility**: Existing functionality preserved with improved quality

### Files Modified
- `utils.py` - Removed pyrubberband integration, streamlined speed factor processing
- `api_models.py` - Updated validation and model_validator for Pydantic v2 compatibility
- `config.yaml` - Added speed factor configuration section with global defaults
- `docs/api/openapi.yaml` - Updated speed_factor_library enum and descriptions
- `docs/api/API_Documentation.md` - Removed pyrubberband references, updated library descriptions
- `requirements.txt`, `requirements.base.with.versions.txt`, `requirements_frozen.txt` - Updated dependencies

## [1.8.0] - 2025-06-19

### Fixed
- **CRITICAL: Performance Regression Resolved** - Restored TTS generation time from 8-11 minutes back to ~1 minute
- **Root Cause Fixed**: Removed async/await overhead from inherently synchronous TTS model operations
- **Corrected Architecture**: Replaced async core engine with synchronous implementation matching original Chatter.py patterns

### Changed
- **Replaced `core_engine.py`**: Now uses synchronous patterns for optimal performance
- **Replaced `main_api.py`**: Corrected FastAPI implementation with proper synchronous core
- **Moved `test_performance_fix.py`** to `tests/` directory for better organization

### Technical Details
- **Performance Fix**: Direct synchronous `model.generate()` calls instead of async overhead
- **Model Loading**: Uses global model variables matching original Chatter.py approach
- **FastAPI Integration**: Minimal async wrapper only where required by FastAPI
- **Gradio UI**: Successfully mounted at `/ui` endpoint with full functionality

### Validation
- **✅ Performance Test**: Confirmed ~1 minute generation time (10x improvement)
- **✅ API Functionality**: All endpoints working correctly
- **✅ Gradio UI**: Fully functional at `/ui`
- **✅ Backward Compatibility**: All existing functionality preserved

### Deployment
- **Server**: `python main_api.py`
- **API**: `http://localhost:7860/api/v1/`
- **UI**: `http://localhost:7860/ui`
- **Docs**: `http://localhost:7860/docs`

---


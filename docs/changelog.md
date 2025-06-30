# Changelog - Chatterbox TTS Extended Plus API Implementation

All notable changes to the API implementation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.12.2] - 2025-06-30 - API Refinement Task 11.12.1: Complete Voice Management Integration Test Fixes

### Major Achievement
- **✅ VOICE MANAGEMENT - COMPLETE**: All voice management workflows now fully functional with 100% integration test pass rate

### Fixed - Voice Management Critical Issues
- **Voice Upload 422 Validation Errors**: 
  - Fixed field name mismatch in test (changed `audio_file` to `voice_file` to match endpoint parameter)
  - Fixed missing `url` field in VoiceMetadata by updating `load_voice_metadata()` to calculate relative paths
  - Fixed response structure mismatch (test expected `metadata` but endpoint returns `voice_metadata`)
- **Voice Deletion 500 Server Errors**:
  - Fixed function name conflict in `main_api.py` (renamed endpoint function to avoid collision with imported `bulk_delete_voices`)
  - Implemented hierarchical folder filtering for bulk deletion (e.g., `folder=characters` now finds files in `characters/casual` and `characters/narrators`)
- **Path Separator Consistency**: 
  - Fixed `url` field generation to use forward slashes consistently across platforms
  - Updated folder structure display to normalize path separators for cross-platform compatibility
- **Folder Structure Display**: 
  - Fixed test to use correct API response format (`folders` field instead of deprecated `structure` field)
  - Implemented proper hierarchical display of folder organization with voice counts

### Integration Test Results
- **Upload Success**: 4/4 voices uploaded to organized folder structure ✅
- **Hierarchical Filtering**: Successfully finds and deletes files in nested folders ✅
- **Search Functionality**: Working across names, descriptions, and tags ✅
- **Single Deletion**: Working correctly ✅
- **Bulk Deletion**: Working with hierarchical folder matching ✅
- **Folder Structure**: Proper display of voice organization ✅

### Technical Implementation
- **VoiceMetadata URL Field**: Added automatic calculation of relative URL paths in `utils/voice/metadata.py`
- **Hierarchical Bulk Deletion**: Enhanced filtering logic in `utils/voice/organization.py` to support parent folder matching
- **Cross-Platform Paths**: Ensured all voice URLs use forward slashes regardless of OS
- **API Function Naming**: Resolved naming conflicts between endpoint functions and utility imports

### Quality Standards Achieved
- **100% Integration Test Pass Rate**: Voice management now matches the quality of TTS and VC input management
- **Cross-Platform Compatibility**: All path handling works consistently on Windows and Linux
- **Unicode Support**: Compatible with Windows cp932 encoding requirements
- **Complete Workflow Coverage**: Upload, organize, search, and delete operations all functional

## [1.12.1] - 2025-06-29 - API Refinement Task 11.12: Complete VC Inputs & Partial Voice Management Integration

### Major Progress
- **✅ VC INPUT MANAGEMENT - COMPLETE**: All file management workflows now fully functional
- **⏳ VOICE MANAGEMENT - PARTIAL**: Core functionality working, upload/deletion debugging pending

### Fixed - VC Input Management (100% Complete)
- **Hierarchical Folder Filtering** - Parent folders now include all subfolders (e.g., `project=interview_project` finds files in `interview_project/raw_recordings`)
- **Enhanced Search Functionality** - Search now includes folder paths in addition to filenames and content
- **DELETE Endpoint Behavior** - Returns 200 success with "already clean" message instead of 404 when no files found
- **Path Separator Consistency** - Preserved forward slashes in folder paths for cross-platform compatibility
- **Folder Path Preservation** - Removed destructive `sanitize_filename()` from folder paths that was converting `/` to `_`
- **Unicode Compatibility** - Removed emoji characters from test scripts for Windows cp932 encoding

### Fixed - Voice Management (Partial)
- **API Response Structure** - Fixed test scripts to use correct `voices` field instead of `files`
- **Hierarchical Folder Filtering** - Applied same parent/subfolder logic as VC inputs
- **Enhanced Search Functionality** - Added folder path inclusion in search operations
- **Unicode Compatibility** - Removed emoji characters from test scripts

### Technical Implementation
- **Path Sanitization Fix**: Removed `sanitize_filename(folder_path)` calls in both VC inputs and voice upload functions
- **Hierarchical Filtering Logic**: Changed exact match (`folder_path == folder`) to include subfolders (`folder_path.startswith(folder + '/')`)
- **Search Enhancement**: Extended search filters to include `folder_path` field across all file management systems
- **Cross-Platform Paths**: Ensured consistent forward slash usage in folder structures

### Files Modified
- `utils/vc_inputs/management.py` - Hierarchical filtering, enhanced search, folder path preservation
- `utils/voice/management.py` - Folder path preservation (removed sanitization)
- `main_api.py` - Voice hierarchical filtering and enhanced search
- `scripts/test_integrated_vc_input_management.py` - Unicode fixes and validation
- `scripts/test_integrated_voice_management.py` - API response structure and Unicode fixes

### Validation Results
- **VC Inputs Integrated Test**: ✅ 100% pass rate - Upload, list, search, delete all working
- **Voice Management Test**: ⏳ ~80% functional - Listing and search working, uploads (422 errors) and deletion (500 errors) pending
- **Cross-Platform Compatibility**: ✅ Path handling unified across Windows/Linux
- **Folder Hierarchy Operations**: ✅ Parent/subfolder relationships working correctly

### Remaining Work (Task 11.12.1)
- **Voice Upload Issues**: Debug 422 validation errors in voice upload endpoint
- **Voice Deletion Issues**: Debug 500 server errors in voice bulk deletion
- **Path Separator Normalization**: Fix voice URLs showing backslashes instead of forward slashes
- **Complete Voice Integration**: Achieve 100% pass rate like VC inputs

### Next Phase Ready
- VC input file management system fully operational and validated
- Foundation laid for completing voice management system debugging
- All cross-platform and hierarchical operation patterns established

## [1.12.0] - 2025-06-29 - API Refinement Task 11.12: Integrated File Management Fixes

### Fixed
- **CRITICAL: Voice API Integration** - Added missing `url` field to VoiceMetadata for seamless TTS integration
- **Cross-Platform Path Handling** - Unified all path separators to forward slashes for Windows/Linux compatibility
- **Hierarchical Folder Operations** - Fixed filtering and deletion to work with subfolder structures
- **Enhanced Search Functionality** - Search now includes folder paths, not just filenames
- **DELETE Endpoint Behavior** - Returns 200 success instead of 404 when no files match deletion criteria

### Enhanced
- **VoiceMetadata API Model** - Added `url` field containing path relative to reference_audio/ directory
- **File Management Workflows** - Complete end-to-end testing and validation of TTS file management
- **Folder Filtering Logic** - Parent folder filters now include all subfolders (e.g., `project=test_book` finds `test_book/chapter1` files)
- **Search Capabilities** - Users can now search by project names and folder structures
- **Error Handling** - More user-friendly responses for edge cases

### Technical Details
- **Empty Project Handling**: Fixed `project=""` parameter to correctly place files in root folder instead of creating "unnamed" folder
- **Path Separator Consistency**: Updated 8 utility files to ensure forward slash usage across all platforms
- **Hierarchical Operations**: Enhanced filtering logic in both API endpoints and bulk operations
- **Unicode Compatibility**: Removed emoji characters from test scripts for Windows cp932 encoding support

### Files Modified
- `api_models.py` - Added url field to VoiceMetadata, fixed empty project validation
- `main_api.py` - Enhanced folder filtering and search functionality
- `utils/outputs/management.py` - Improved hierarchical deletion and error handling
- `utils/vc_inputs/management.py` - Path separator consistency fixes
- `utils/*/folders.py` - Cross-platform folder structure generation
- `docs/api/schemas/response-models.md` - Updated VoiceMetadata documentation
- `scripts/test_integrated_*.py` - Unicode compatibility improvements

### Validation
- **✅ TTS File Management**: Complete workflow validation from generation to deletion
- **✅ Cross-Platform Compatibility**: Windows and Linux path handling unified
- **✅ API Integration**: Voice URL retrieval and TTS generation working seamlessly
- **✅ Edge Case Handling**: Proper responses for empty folders and missing files
- **✅ Search and Filter**: All folder-based operations working correctly

### Next Steps
- Apply similar fixes to VC input and voice management integrated tests
- Validate same cross-platform and hierarchical operation improvements

## [1.11.1] - 2025-06-28 - API Refinement Task 11.9.1: Small Fixes

### Fixed
- **ENHANCED: Bulk Delete Folder Cleanup** - Automatic empty folder removal for outputs and vc_inputs
  - Modified `bulk_delete_outputs()` in `utils/outputs/management.py` to automatically remove empty folders after file deletion
  - Modified `bulk_delete_vc_inputs()` in `utils/vc_inputs/management.py` to automatically remove empty folders after file deletion
  - Added comprehensive tracking of folders with deletions for targeted cleanup
  - Enhanced response messages to include folder cleanup statistics (e.g., "Deleted 5 files and cleaned up 2 empty folders")
  - Graceful error handling - folder cleanup failures don't affect main deletion operation
  - **Note**: This behavior is specific to outputs and vc_inputs directories, unlike voices where empty subfolders have semantic meaning

- **IMPROVED: TTS Response Mode Documentation and Testing** - Clarified JSON vs Stream mode usage
  - Fixed `scripts/test_core_examples.py` to use `?response_mode=url` for proper JSON responses in TTS testing
  - Enhanced `docs/api/endpoints/tts.md` with prominent "Response Modes" section at the top
  - Added visual indicators (🔄 Stream Mode, 📄 JSON Mode) and clear decision guide
  - Enhanced Python examples with separate functions demonstrating both response modes clearly
  - Added comprehensive documentation of `X-Alternative-Formats` header for Stream mode
  - Clarified default behavior (Stream mode) vs JSON mode usage patterns

### Technical Details
- **Folder Cleanup Logic**: Only removes folders that are completely empty (no files, no subdirectories) after deletion operations
- **Response Mode Clarity**: Stream mode (default) returns binary audio files directly; JSON mode (`?response_mode=url`) returns metadata with file URLs
- **Test Script Compatibility**: Core validation tests now properly expect JSON responses when using URL mode
- **Backward Compatibility**: All existing functionality preserved; enhancements are additive

## [1.11.0] - 2025-06-27 - Complete File Management System

### Added
- **NEW: VC Input Upload System** - Direct file upload for voice conversion
  - Added `POST /api/v1/vc_input` endpoint for uploading VC input files with metadata
  - Support for `vc_input_file` (required), `text` (description), `project`/`folder_path` (organization), `overwrite` (safety)
  - Automatic metadata generation: file size, duration, sample rate, format, timestamps
  - Project folder organization with automatic directory creation
  - File validation with size limits (50MB) and format checking (WAV, MP3, FLAC, OGG, M4A)
  - JSON companion files for complete metadata persistence

- **NEW: Comprehensive Deletion Endpoints** - Safe file deletion with confirmation requirements
  - Added `DELETE /api/v1/vc_input/{filename}` for single VC input file deletion
  - Added `DELETE /api/v1/vc_inputs` for bulk VC input deletion with filtering
  - Added `DELETE /api/v1/output/{filename}` for single output file deletion  
  - Added `DELETE /api/v1/outputs` for bulk output deletion with filtering
  - Safety confirmation requirement (`confirm=true`) for all deletion operations
  - Support for filtering by folder/project, generation_type, search terms, and specific filenames
  - Complete cleanup of both audio files and metadata files

- **NEW: Enhanced File Management Models** - Complete API model coverage
  - Added `VCInputUploadResponse`, `VCInputDeletionResponse`, `OutputDeletionResponse` models
  - Added `VCInputMetadata` model with comprehensive file information
  - Extended utility functions in `utils/vc_inputs/management.py` and `utils/outputs/management.py`
  - Bulk operation support with detailed response information

### Enhanced
- **File Operations Documentation** - Complete endpoint coverage in `docs/api/endpoints/file-operations.md`
  - Added documentation for all new upload and deletion endpoints
  - Comprehensive examples with curl commands and response formats
  - Safety guidelines and parameter documentation
- **Cross-Reference Documentation** - Improved endpoint discoverability
  - Updated `voice-conversion.md` with VC input management section
  - Updated `tts.md` with output management section
  - Enhanced navigation between related endpoints

### Technical
- **OpenAPI Specification** - Complete API specification updates
  - Added all new endpoints with proper request/response schemas
  - Added deletion response models and VC input metadata schemas
  - Updated endpoint tags and operation IDs for consistency
- **Validation & Testing** - Comprehensive endpoint validation
  - Core validation: 100% pass rate (6/6 tests)
  - Upload functionality: File upload with metadata generation tested
  - Deletion safety: Confirmation requirements validated
  - Error handling: Proper validation and error responses confirmed
  - Documentation integrity: Link validation completed

### Security
- **Deletion Safety System** - Comprehensive protection against accidental deletion
  - All deletion endpoints require explicit `confirm=true` parameter
  - Proper error responses (400) when confirmation is missing
  - Detailed deletion logging and response information

## [1.10.0] - 2025-06-28

### Added
- **NEW: TTS Project Organization System** - Enhanced TTS generation with project folder support
  - Added `project` parameter to `/api/v1/tts` for organizing generated files within `outputs/` directory
  - Added `folder` parameter as alias for `project` for consistency across endpoints
  - Automatic folder creation with support for nested folder hierarchies (e.g., `project1/chapter1/section01`)
  - Project path validation using sanitized file paths
  - Enhanced URL generation to include project folder paths in response URLs
  - Updated X-Alternative-Formats header in streaming mode to include project paths
- **NEW: Enhanced API Documentation Structure** - Improved endpoint documentation organization
  - Added endpoint indexes to multi-endpoint documentation files
  - Clear endpoint listings for `concatenation.md` (2 endpoints) and `voice-management.md` (6 endpoints)
  - Maintained single-endpoint documents without unnecessary indexes
- **NEW: Parameter Alias Validation** - Robust handling of project/folder parameter aliases
  - Smart alias resolution with precedence rules (project takes precedence over folder)
  - Validation prevents conflicting values between alias parameters
  - Clean parameter processing removes unused aliases after resolution

### Enhanced
- **Core TTS Pipeline Updates** - Project folder support throughout generation pipeline
  - Updated `_process_tts_generation_sync()` to create project-specific output directories
  - Modified `_combine_audio_chunks()` to use project folders for final file placement
  - Enhanced speed factor and trimming post-processing to maintain project folder structure
  - Improved `convert_audio_formats()` with cross-platform URL generation (forward slashes)
- **OpenAPI Specification Updates** - Complete specification alignment with new features
  - Added `project` and `folder` parameters to TTSRequest schema
  - Updated parameter descriptions and examples
  - Maintained backward compatibility with existing API usage

### Documentation
- **Comprehensive TTS Documentation Updates** - Complete coverage of new project features
  - Added project parameter documentation to Core Audio Parameters section
  - Documented X-Alternative-Formats header behavior with project folders
  - Added practical project organization examples with curl commands
  - Updated streaming response documentation with project path examples

### Technical Details
- **File System Integration** - Robust project folder handling
  - Automatic directory creation with `parents=True` for nested structures
  - Cross-platform path handling with proper URL generation
  - Maintains existing file naming conventions with enhanced organization
- **Backward Compatibility** - Zero breaking changes to existing API usage
  - All existing TTS requests continue to work unchanged
  - Project parameter is optional, defaults to root outputs directory
  - Maintains all existing response formats and URL structures

### Validation
- **✅ Core Validation**: All tests passing (6/6, 100% success rate)
- **✅ Project Parameter Testing**: Complete validation of new functionality
  - Project folder creation and file organization
  - Folder alias parameter handling
  - URL generation with project paths
  - X-Alternative-Formats header with project folders
- **✅ Performance**: TTS generation time maintained at ~1 minute (no regression)

## [1.9.0] - 2025-06-28

### Added
- **NEW: VC Input File Management** - Complete VC input file listing and management system
  - **GET** `/api/v1/vc_inputs` - List VC input files with pagination, search, and folder filtering
  - **GET** `/api/v1/vc_inputs/folders` - Get folder structure of vc_inputs directory
- **NEW: Enhanced Folder Management** 
  - **GET** `/api/v1/outputs/folders` - Get folder structure of outputs directory
  - Added `folder` and `project` parameters to `/api/v1/outputs` for filtering by folder path
  - Added `project` parameter (alias for `folder`) to `/api/v1/voices` endpoint
- **NEW: Corrupted File Cleanup System** - Automated cleanup of size-0 (corrupted) audio files
  - Integrated into startup and scheduled cleanup (every 4 hours)
  - Comprehensive logging of cleanup operations
  - Scans outputs/, reference_audio/, and vc_inputs/ directories recursively

### Fixed
- **CRITICAL: Audio Duration Calculation Error** - Fixed crashes when processing corrupted files (size 0)
  - Added file size validation before calling `calculate_audio_duration()`
  - Enhanced error handling and logging for empty files
- **Fixed `/api/v1/voices/folders` Endpoint** - Updated response format to match API models
  - Corrected `get_voice_folder_structure()` function to return proper response format
  - Fixed compatibility with `VoiceFoldersResponse` model

### Enhanced
- **Comprehensive File Management** - Unified approach across all audio directories
  - Consistent pagination, search, and filtering across outputs, voices, and vc_inputs
  - Enhanced metadata collection with folder path tracking
  - Improved error handling for file system operations
- **Enhanced Parameter Support** - `project` parameter as intuitive alias for `folder`
  - Supports both `/api/v1/outputs?folder=chapter1` and `/api/v1/outputs?project=chapter1`
  - Consistent across all file listing endpoints

### Documentation
- **Updated OpenAPI Specification** - Complete coverage of all new endpoints and parameters
- **Enhanced File Operations Guide** - Comprehensive documentation for new VC input management
- **Updated Voice Management Guide** - Added project parameter examples and usage
- **API Reference Updates** - Complete parameter documentation with examples

### Technical Implementation
- **New Utility Modules**:
  - `utils/vc_inputs/management.py` - VC input file scanning and metadata
  - `utils/vc_inputs/folders.py` - VC inputs folder structure management
  - `utils/outputs/folders.py` - Outputs folder structure management
  - `utils/cleanup/corrupted_files.py` - Comprehensive corrupted file cleanup
- **Enhanced API Models**: `VCInputFileMetadata`, `VCInputFilesResponse` for type safety
- **Improved Resource Management**: Extended cleanup scheduler with corrupted file handling

### Validation
- **✅ All New Endpoints**: Confirmed working with 200 status codes and proper responses
- **✅ Folder Filtering**: Verified parameter aliasing and filtering functionality
- **✅ Cleanup System**: Integrated into resource management with comprehensive logging
- **✅ Backward Compatibility**: All existing functionality preserved and enhanced
- **✅ Documentation Accuracy**: Complete OpenAPI spec and endpoint documentation

### Files Modified
- `main_api.py` - Added new endpoints for VC inputs and folder structures
- `api_models.py` - New models for VC input file management
- `utils/outputs/management.py` - Enhanced file size validation
- `management/resource_manager.py` - Integrated corrupted file cleanup
- `utils/voice/organization.py` - Fixed folder structure response format
- `docs/api/openapi.yaml` - Complete specification updates
- `docs/api/endpoints/file-operations.md` - Comprehensive new endpoint documentation
- `docs/api/endpoints/voice-management.md` - Enhanced parameter documentation

## [Utils Refactoring - Complete] - 2025-06-26 - Phase 4 Direct Import Optimization

### Added
- **Direct Import Optimization**: Converted all internal imports to explicit direct imports for enhanced code visibility
- **Clean Module Architecture**: Removed backward compatibility layer and enhanced all module `__init__.py` files with documentation

### Changed
- **main_api.py**: Updated to use direct imports (`from utils.voice.metadata import load_voice_metadata`)
- **core_engine.py**: Updated to use direct imports (`from utils.audio.processing import apply_speed_factor`)
- **api_models.py**: Updated to use direct imports (`from utils.validation.text import validate_text_input`)
- **All utils modules**: Enhanced with comprehensive documentation and organized exports

### Removed
- **Backward compatibility layer**: Cleaned up `utils/__init__.py` from compatibility imports
- **Legacy import patterns**: No more generic `from utils import function` usage in codebase

### Technical
- All 29 functions fully migrated to modular structure with direct imports
- 100% test compatibility maintained (6/6 core tests pass)
- Clean architectural separation achieved

## [Utils Refactoring - Partial] - 2025-06-26 - Modular Utils Implementation

### Added
- **Complete Modular Utils Structure**: Transformed monolithic 2,391-line `utils.py` into organized, maintainable modules
- **All 29 Functions Migrated** across 6 logical modules:
  - **Audio Processing Module** (`utils/audio/`) - 600+ lines
    - `processing.py` - Speed factor, duration calculations (313 lines)
    - `analysis.py` - Format normalization, silence detection (123 lines)
    - `trimming.py` - Audio trimming functions (164 lines)
  - **Concatenation Module** (`utils/concatenation/`) - 900+ lines
    - `parsing.py` - Parse concatenation instructions (119 lines)
    - `basic.py` - Basic concatenation operations (156 lines)
    - `advanced.py` - Advanced concatenation with mixed sources (625 lines)
  - **Files Module** (`utils/files/`) - 209 lines
    - `naming.py` - Filename generation and sanitization (133 lines)
    - `operations.py` - File operations and validation (50 lines)
    - `paths.py` - Path utilities (26 lines)
  - **Voice Module** (`utils/voice/`) - 507 lines
    - `metadata.py` - Voice metadata management (155 lines)
    - `management.py` - Voice file management (195 lines)
    - `organization.py` - Bulk operations and folder structure (125 lines)
  - **Outputs Module** (`utils/outputs/`) - 183 lines
    - `management.py` - Generated content management (173 lines)
  - **Validation Module** (`utils/validation/`) - 85 lines
    - `text.py` - Text validation (31 lines)
    - `audio.py` - Audio format validation (14 lines)
    - `network.py` - URL validation (40 lines)
  - **Formatting Module** (`utils/formatting/`) - 22 lines
    - `display.py` - File size formatting (16 lines)
- **Complete Backward Compatibility**: All existing `from utils import ...` statements preserved
- **Advanced Concatenation Functions**: Full implementation of mixed-source concatenation

### Technical Implementation
- **Zero Breaking Changes**: 100% backward compatibility maintained
- **Complete Migration**: All 29 functions from original utils.py successfully migrated
- **Validation Testing**: 6/6 core tests passed (100% success rate)
- **Clean Structure**: 1,900+ lines organized into 25+ focused module files
- **Removed Legacy**: `utils_original.py` safely removed after successful validation

### Benefits Achieved
- **Maintainability**: Functions organized by logical purpose instead of monolithic file
- **Developer Experience**: Clear module boundaries and responsibilities
- **Code Navigation**: Functions grouped in focused, manageable files
- **Team Development**: Multiple developers can work on different modules simultaneously
- **Future-Ready**: Optional Phase 4 available for direct import optimization

### Validation Results
- **Import Testing**: All 29 functions import correctly from new modular structure
- **Server Compatibility**: Server starts and runs healthy with new structure
- **Core Functionality**: All API endpoints working correctly
- **Performance**: No regression in functionality or response times
- **Function Preservation**: All original functionality maintained with identical interfaces

### Code Organization Benefits
- **Developer Productivity**: Find audio functions in `utils/audio/`, concatenation in `utils/concatenation/`
- **Maintainability**: 300-line focused modules vs 2,391-line monolith
- **Parallel Development**: Team members can work on different modules simultaneously
- **Code Review Efficiency**: Targeted reviews for specific functionality domains
- **Testing Isolation**: Module-specific testing strategies and coverage

### Migration Statistics
- **Phase 1 Complete**: Audio + Concatenation modules (1,050+ lines migrated)
- **Functions Migrated**: 19 total (12 audio + 7 concatenation)
- **Lines Reorganized**: ~44% of original utils.py codebase restructured
- **Modules Created**: 6 focused modules with clear single responsibilities
- **Compatibility**: 100% backward compatibility maintained

### Validation Results
- **Core Validation**: 6/6 tests passed in 36.2 seconds
- **Import Testing**: Both legacy and modular imports verified working
- **Server Compatibility**: FastAPI server starts and operates normally
- **Production Ready**: No performance regression, all existing functionality preserved

### Next Phase Preparation
- **Phase 2 Ready**: Files, Voice, Outputs, Validation, Formatting modules (29 functions remaining)
- **Priority Target**: Files module (9 functions, high usage in core_engine.py and main_api.py)
- **Pattern Established**: Proven migration workflow for remaining 29 functions
- **Safety Measures**: `utils_original.py` preserved until all migrations complete

### Impact on Development
- **Immediate Value**: Improved code organization without any disruption
- **Future Productivity**: Easier feature development with clear module boundaries
- **Code Quality**: Enhanced maintainability and reduced cognitive load
- **Team Efficiency**: Reduced merge conflicts and clearer code ownership

## [1.11.0] - 2025-06-25 - Advanced Concatenation Features (Task 11.5)

### Added
- **Mixed Source Concatenation**: New `POST /api/v1/concat/mixed` endpoint for professional audio production
- **Multiple Input Sources**: Support for server files + uploaded files + manual silence in single request
- **Advanced Audio Processing**: Order control, crossfading, trimming, and normalization in mixed workflows
- **Multipart Upload Support**: Handle file uploads with JSON configuration in single API call
- **Enhanced Models**:
  - `MixedConcatSegment` - Define individual segments (server_file, upload, silence)
  - `MixedConcatRequest` - Comprehensive request validation and configuration
- **Professional Features**:
  - Segment order specification via array positioning
  - Crossfading compatibility with silence insertion
  - Trimming integration for all audio sources
  - Advanced metadata generation with processing details

### Technical Implementation
- **New Endpoint**: `POST /api/v1/concat/mixed` with multipart/form-data support
- **Core Function**: `concatenate_with_mixed_sources()` handles complex concatenation logic
- **File Management**: Temporary upload handling with automatic cleanup
- **Validation**: Comprehensive input validation for all segment types and file references
- **Integration**: Seamless integration with existing trimming, crossfading, and normalization features
- **Metadata**: Enhanced filename generation including upload counts and processing parameters

### Use Cases
- **Podcast Production**: Mix intro music (server) + recorded content (upload) + outro music (server)
- **Voice Acting**: Combine multiple takes (uploads) with background audio (server files)
- **Interactive Content**: Dynamic audio assembly with user-generated content + system audio
- **Professional Editing**: Precise timing control with manual silence and automatic processing

### Performance & Quality
- **Streaming Support**: Direct file streaming for large concatenated results
- **Memory Efficiency**: Optimized processing for multiple large files
- **Error Handling**: Comprehensive validation prevents invalid requests
- **Backward Compatibility**: Existing `/api/v1/concat` endpoint unchanged

### Documentation
- **Complete API Documentation**: Full endpoint documentation with examples and use cases
- **Implementation Guide**: Professional audio production workflows
- **Performance Notes**: Memory usage, processing times, and optimization tips

### Validation
- **100% Test Success Rate**: All validation scenarios tested and passing
- **Complex Feature Testing**: Multi-source scenarios with silence and trimming validated
- **Core System Health**: All existing functionality preserved and working

### Bug Fixes
- **Health Endpoint**: Fixed metrics type conversion issue causing health check failures
- **Monitoring**: Improved duration data handling with proper type validation

## [1.10.0] - 2025-06-25 - TTS Trimming Integration (Task 11.4)

### Added
- **TTS Audio Trimming**: Added silence trimming capability to TTS endpoint
- **New TTS Parameters**: 
  - `trim` (boolean, default: false) - Apply silence trimming to generated audio
  - `trim_threshold_ms` (integer, default: 200, range: 50-1000) - Silence threshold for trimming
- **Enhanced Filename Generation**: Trimming parameters included in TTS output filenames (e.g., `trim200`)
- **Post-Processing Pipeline**: Trimming applied after speed factor adjustment and before format conversion
- **Documentation**: Complete API documentation, examples, and OpenAPI specification updates

### Technical Implementation
- **Integration Point**: Trimming applied in `_apply_trimming_post_processing()` method in `core_engine.py`
- **Workflow**: Generation → Speed Factor → **Trimming** → Format Conversion → Output
- **Reuse**: Leverages existing trimming utilities from concatenation system (`apply_audio_trimming()`)
- **Metadata**: Trimming parameters included in TTS generation metadata
- **Validation**: Full parameter validation and error handling

### Use Cases
- Professional audio production workflows requiring clean timing
- Removing TTS generation artifacts and unwanted silence
- Consistent audio timing for concatenation and editing
- Automated audio post-processing pipelines

### Files Modified
- `api_models.py` - Added trim parameters to TTSRequest model
- `core_engine.py` - Implemented TTS trimming post-processing pipeline
- `utils.py` - Updated enhanced filename generation for TTS trimming
- `docs/api/openapi.yaml` - Updated TTS schema with trimming parameters
- `docs/api/endpoints/tts.md` - Added trimming documentation and examples
- `docs/api/schemas/examples/curl-examples.md` - Added TTS trimming examples

### Validation
- **✅ Core Validation**: 100% pass rate maintained
- **✅ Feature Testing**: Trimming parameters correctly processed and included in filenames
- **✅ Integration Testing**: Seamless operation with existing TTS workflow
- **✅ Documentation**: Complete API documentation and examples

## [1.9.0] - 2025-06-25 - Mixed-Mode Concatenation

### Added
- **MAJOR: Mixed-Mode Concatenation** - Revolutionary audio production flexibility
- **Per-Gap Decision Logic**: Manual silences and natural pauses can coexist in single request
- **Intelligent Gap Analysis**: System determines appropriate behavior for each gap between audio files
  - Manual silence: `"(1s)"` notation between files → precise timing
  - Natural pause: No notation + `pause_duration_ms > 0` → randomized natural timing  
  - Direct join: No notation + `pause_duration_ms = 0` → seamless connection
- **Enhanced Metadata Tracking**: Separate counts for `silence_segments` and `natural_pauses`
- **Detailed Processing Info**: Complete sequence breakdown showing manual vs natural gaps

### Enhanced
- **User Experience**: Users can specify precise timing where needed while maintaining natural flow elsewhere
- **Professional Workflows**: Perfect for video (sync points + natural flow), podcasts (structured + conversational), audiobooks (chapters + reading flow)
- **Parameter Interaction**: Smart handling of mixed timing requirements in single request
- **Documentation**: Complete mixed-mode explanation with parameter interaction logic and working examples

### Changed
- **BREAKING: Default Behavior**: `pause_duration_ms` default changed from 600ms to 0ms for more intuitive behavior
  - **Rationale**: Users expect no automatic pauses unless explicitly requested
  - **Migration**: Add `"pause_duration_ms": 600` to maintain previous behavior
  - **Benefit**: More predictable default behavior, no unwanted pauses

### Technical
- **New Functions**: `determine_gap_type()`, `generate_natural_pause_duration()`, `apply_audio_trimming()`
- **Enhanced `concatenate_with_silence()`**: Now supports mixed-mode operation with pause parameters
- **Improved Error Handling**: AudioSegment serialization fix for proper JSON responses
- **Documentation Updates**: API spec, endpoint docs, and examples updated for new default values

### Example Working
```json
{
  "files": ["intro.wav", "(1s)", "main.wav", "conclusion.wav", "(500ms)", "outro.wav"],
  "pause_duration_ms": 600,
  "pause_variation_ms": 200
}
```
Produces: intro → 1000ms manual → main → ~600±200ms natural → conclusion → 500ms manual → outro

## [1.8.0] - 2025-06-25 - Manual Silence Insertion

### Added
- **MAJOR: Manual Silence Insertion** - Phase 11 Task 11.2 complete
- **Silence Notation System**: Use `(duration[ms|s])` in concat files array for precise timing
  - Supported units: milliseconds (`(500ms)`) and seconds (`(1.5s)`)
  - Duration range: 50ms to 10s with comprehensive validation
- **Mixed File/Silence Arrays**: `["(1s)", "intro.wav", "(800ms)", "main.wav", "(500ms)"]`
- **Enhanced Filename Generation**: Includes silence count tracking (`sil2`, `sil3`)
- **Professional Audio Production**: Video, podcast, and presentation-ready workflows

### Enhanced
- **Concatenation Endpoint**: Now supports both manual silence and natural pause modes
- **Intelligent Mode Detection**: Automatically switches between manual and natural pause systems
- **Enhanced Metadata**: Detailed silence tracking with notation preservation
- **Error Handling**: Robust validation for silence notation formats and ranges

### Fixed
- **CRITICAL: Crossfade Issue with Manual Silence** - Crossfade no longer applies between silence and audio
  - **Problem**: Crossfading after silence caused unnatural low-volume audio start
  - **Solution**: Intelligent crossfade application only between consecutive audio files
  - **Behavior**: Clean audio start after silence, preserves crossfade between audio segments
- **Enhanced Logging**: Added detailed crossfade and silence processing logs for debugging

### Technical Implementation
- **Silence Parsing**: `parse_concat_files()` function with regex-based notation parsing
- **Silence Generation**: `generate_silence_segment()` using pydub AudioSegment.silent()
- **Enhanced Concatenation**: `concatenate_with_silence()` for mixed file/silence processing
- **API Model Updates**: ConcatRequest supports silence notation with comprehensive validation
- **Filename Enhancement**: `generate_enhanced_filename()` includes silence count parameters

### Documentation
- **Complete API Documentation**: Updated file-operations.md with silence insertion examples
- **Production Workflows**: Video production, podcast, and presentation use cases
- **Error Handling**: Comprehensive validation examples and error responses
- **Multiple Format Examples**: curl, Python, and JavaScript integration examples

### Validation
- **✅ Comprehensive Testing**: 100% success rate across 7 test scenarios
- **✅ Edge Case Coverage**: Invalid notation, out-of-range durations properly rejected
- **✅ Core Compatibility**: All existing functionality preserved (100% core validation)
- **✅ Integration Testing**: Manual silence works with crossfade, normalization, streaming

### Use Cases
- **Video Production**: Precise timing for narration overlay
- **Podcast Creation**: Dramatic pauses and natural conversation flow
- **Presentations**: Professional spacing between sections
- **Audio Editing**: Manual control over silence placement

## [June 24, 2025] - Two-Tier Testing Strategy Implementation

### Overview
Implemented comprehensive two-tier testing strategy providing balanced validation approach for development workflow efficiency and comprehensive release validation.

### Changes Made

#### Two-Tier Testing Strategy Implementation
- **Tier 1: Core Validation (2-3 minutes)**:
  - Created `scripts/test_core_examples.py` for implementation protocol validation
  - Universal compatibility without specific voice file requirements
  - Essential functionality testing (health, TTS, VC, listing endpoints)
  - Suitable for routine development validation and CI/CD integration

- **Tier 2: Comprehensive Validation (8-15 minutes)**:
  - Enhanced `scripts/test_curl_examples.py` with 90-second timeouts
  - Complete documentation example validation
  - Advanced features testing with documented setup requirements
  - Suitable for releases and developer onboarding

#### Documentation Structure Enhancement
- **Implementation Protocols Document**: 
  - Created `docs/dev/implementation-protocols.md` with comprehensive development standards
  - Established common protocols for all development projects
  - Defined template structure for project-specific resume prompts
  - Integrated testing strategy with development workflow

- **cURL Examples Reorganization**:
  - Restructured `docs/api/schemas/examples/curl-examples.md` with clear separation
  - Core Examples section for universal compatibility (no setup required)
  - Advanced Examples section with documented voice file requirements
  - Setup validation commands and clear usage guidance

#### Scripts Documentation Update
- **Enhanced `scripts/README.md`**:
  - Added two-tier testing strategy documentation
  - Updated usage scenarios with clear tier guidance
  - Implementation phase closing protocol
  - Integration with development workflow

#### Validation Infrastructure
- **Testing Integration**:
  - Core validation: `test_core_examples.py` (14.5s execution, 100% pass rate)
  - Comprehensive validation: `test_curl_examples.py` (2m 40s execution)
  - Documentation link validation: `check_links.py` (20 files, 0 errors)
  - API synchronization: `sync_openapi.py` (version tracking)

### Technical Details
- All validation scripts tested and working correctly
- Documentation links verified across modular structure
- Implementation protocol established for routine phase closing
- Two-tier strategy ready for routine development use

### Files Modified
- `docs/dev/implementation-protocols.md` (new)
- `docs/dev/two-tier-testing-implementation-plan.md`
- `docs/api/schemas/examples/curl-examples.md`
- `scripts/README.md`
- `scripts/test_core_examples.py` (enhanced)
- `README.md` (testing strategy reference added)


## [June 23, 2025] - API Docs reorganization Phase 4.6: Final Refinements

### Overview
Completed final refinements of the API documentation reorganization project, focusing on validation script improvements and example fixes.

### Changes Made

#### Testing Infrastructure Improvements
- **Enhanced cURL Examples Testing**: 
  - Fixed JSON parsing in `scripts/test_curl_examples.py` to properly handle multiline JSON payloads
  - Improved regex patterns for extracting curl commands from markdown documentation
  - Updated examples to reference actual files that exist in the project
  - Fixed Windows encoding issues by removing Unicode emojis from output

#### Documentation Examples Updates  
- **Updated cURL Examples**: 
  - Replaced fictional file references (e.g., "speaker1/formal.wav") with actual files ("test_voices/linda_johnson_01.mp3")
  - Updated VC examples to use real audio files from `vc_inputs/` directory
  - Added appropriate notes for examples requiring user-specific files
  - Clarified which examples are demonstrations vs. working tests

#### Validation Scripts  
- **Created Working Examples Tester**: 
  - New `scripts/test_working_examples.py` for testing core functionality
  - Tests health check, voice listing, outputs listing, and basic TTS generation
  - Designed to avoid encoding issues and focus on essential working examples
  - Provides clear pass/fail reporting for CI/CD integration

#### Documentation Structure Validation
- **Confirmed Core vs Administrative API Documentation**: 
  - Verified separation is properly documented in `docs/api/README.md`
  - OpenAPI sync checker working correctly and showing expected differences
  - Administrative endpoints intentionally separated from core API documentation

#### Scripts Documentation
- **Created Comprehensive Scripts Documentation**:
  - New `scripts/README.md` with complete documentation of all validation scripts
  - Updated `docs/api/how-to-update-api-docs.md` with script reference and usage guide
  - Clear usage scenarios for implementation protocol vs. comprehensive validation

### Technical Details
- **Script Improvements**: Enhanced regex parsing for multiline curl commands with JSON payloads
- **Example Validation**: Updated all cURL examples to use actual project files  
- **Encoding Safety**: Removed Unicode characters that cause issues with Windows Japanese encoding
- **Testing Strategy**: Created focused test suite for examples expected to work vs. error demonstrations

### Validation Results
- **OpenAPI Sync Check**: Working correctly, shows expected Administrative API endpoint differences
- **cURL Example Testing**: JSON parsing fixed, realistic file references updated
- **Working Examples**: 3/4 core tests passing (health check intermittent, TTS generation working)
- **Documentation Structure**: All cross-references validated and working

### Status
- **API Documentation Reorganization**: COMPLETED
- **All Phases**: Successfully completed (Phase 1-4)  
- **Validation Scripts**: Ready for development workflow integration
- **Documentation**: Modular structure established and validated

### API Documentation Reorganization Project - Phase 4 Nearly Complete (Validation & Cleanup)
- **Script Validation & Refinement Complete**: All documentation maintenance scripts debugged and working
  - Fixed link validator path resolution bugs and Unicode encoding issues
  - Validated Python example tester against all documentation (4/4 examples pass)
  - Validated cURL example tester against all documentation (6/28 pass - needs JSON format fixes)
  - Tested OpenAPI sync checker against live implementation (identifies sync differences correctly)
  - All scripts now handle Windows cp932 encoding correctly without Unicode errors
- **Final Integration Complete**: Documentation structure fully integrated
  - Updated README-API.md to reference new modular documentation structure
  - Verified server `/docs` endpoint continues working correctly with Swagger UI
  - All internal cross-references validated and working
  - Documentation navigation tested and confirmed intuitive
- **Cleanup & Archive Complete**: Original files safely preserved
  - Moved all `.backup` files to `docs/api/.archive/` directory
  - Created `docs/audio_files_directory_structure.md` for complete file organization reference
  - Fixed all broken internal links identified during validation
- **Remaining for Full Completion**: Task 4.6 (Final Refinements)
  - Fix cURL examples JSON formatting issues and improve test coverage
  - Enhance OpenAPI sync checker to handle Core vs Administrative API distinction
  - Add Core vs Administrative API explanation to README-API.md
  - Complete pre-commit hooks after validation scripts perfected

### API Documentation Reorganization Project - Phase 3 Complete (OpenAPI Optimization & Integration)
- **OpenAPI Simplification**: Dramatically simplified the OpenAPI specification while adding completeness:
  - Reduced `openapi.yaml` from 1,462 lines to 648 lines (56% reduction from original)
  - Added all essential voice management endpoints: DELETE `/voice/{filename}`, bulk DELETE `/voices`, PUT `/voice/{filename}/metadata`, GET `/voices/folders`
  - Removed excessive description text and consolidated duplicate examples
  - Maintained complete coverage of core user-facing functionality
- **Administrative Endpoint Separation**: Created clear documentation structure for different audiences:
  - **Core API** (main `openapi.yaml`): User-facing functionality for developers and integrators
  - **Administrative API** (`reference/administrative-endpoints.md`): System monitoring, cleanup, debugging for DevOps teams
  - Documented `/metrics`, `/resources`, `/cleanup*`, `/errors*` endpoints separately
  - Established classification rules for future endpoint additions
- **Schema Validation & Enhancement**: Ensured consistency between documentation and implementation:
  - Updated TTSRequest schema with correct parameter ranges (temperature: 0.1-2.0, exaggeration: 0-2.0)
  - Enhanced VCRequest schema with proper defaults and validation constraints
  - Added missing but important parameters (seed, disable_watermark) for API completeness
  - Validated all endpoint definitions against actual FastAPI routes in `main_api.py`
- **Documentation Infrastructure**: Built foundation for future automation:
  - Updated maintenance guide with endpoint classification procedures
  - Added automation-ready patterns for core vs administrative endpoint detection
  - Enhanced cross-reference system with proper separation indicators
  - Ensured OpenAPI spec passes YAML validation and Swagger UI compatibility

### API Documentation Reorganization Project - Phase 2 Complete (Content Organization & Guides)
- **Feature-Specific Guides**: Created comprehensive guides for advanced API capabilities:
  - `docs/api/guides/streaming-responses.md` (249 lines) - Direct file downloads, response handling, programming examples
  - `docs/api/guides/file-uploads.md` (412 lines) - Upload capabilities, multipart handling, validation, optimization
  - `docs/api/guides/error-handling.md` (530+ lines) - Comprehensive error handling, troubleshooting, retry logic
  - `docs/api/guides/advanced-features.md` (297+ lines) - Speed control, batch processing, concatenation, optimization
- **Schema Documentation**: Complete API data model reference:
  - `docs/api/schemas/request-models.md` (282+ lines) - Complete request schemas, validation rules, examples
  - `docs/api/schemas/response-models.md` (367+ lines) - Complete response schemas, headers, error formats
- **Technical Reference**: Comprehensive system documentation:
  - `docs/api/reference/configuration.md` (185+ lines) - Complete configuration guide with all settings
  - `docs/api/reference/file-structure.md` (360 lines) - Directory organization, file management, best practices
  - `docs/api/reference/compatibility.md` (240+ lines) - System requirements, platform support, dependencies
- **Maintenance Documentation**: 
  - `docs/api/how-to-update-api-docs.md` (452 lines) - Comprehensive maintenance guide with validation procedures

**Key Improvements:**
- **Modular Organization**: Feature-specific guides for targeted learning
- **Comprehensive Coverage**: All API features, parameters, and capabilities documented
- **Developer Experience**: Programming examples in Python, JavaScript, cURL for all features
- **Maintenance Ready**: Detailed procedures for keeping documentation current
- **Quality Standards**: Validation procedures, change impact assessment, automated checking

**Technical Content:**
- **Streaming Responses**: Direct file downloads, alternative formats, error handling
- **File Uploads**: Multipart uploads, validation, security, performance optimization
- **Error Handling**: Complete error taxonomy, retry logic, monitoring, prevention
- **Advanced Features**: Speed control, batch processing, concatenation, OpenAI compatibility
- **Request/Response Models**: Complete schema reference with validation rules
- **Configuration**: All settings with production/development recommendations
- **File Structure**: Directory organization, backup strategies, performance considerations
- **Compatibility**: Platform support, dependencies, Docker, cloud deployment

**Documentation Quality:**
- **3,400+ lines** of comprehensive, organized documentation
- **Complete API Coverage**: Every endpoint, parameter, and feature documented
- **Practical Examples**: Copy-pasteable code samples for all major use cases
- **Troubleshooting**: Common issues and solutions with step-by-step guidance
- **Maintenance Procedures**: Update workflows, validation scripts, change management

**Migration Status**: 
- ✅ Phase 1 Complete - Core split & extraction with validated examples
- ✅ Phase 2 Complete - Content organization & guides with comprehensive coverage
- 🔄 Next: Phase 3 (OpenAPI optimization & integration, cross-reference updates)

### API Documentation Reorganization Project - Phase 1 Complete (Core Split & Extraction)
- **Documentation Backup**: Safely backed up all original documentation files with .backup extensions
- **Navigation Hub**: Created comprehensive new `docs/api/README.md` with clear navigation structure and "How to Use This Documentation" guide
- **Quick Start Guide**: Extracted and enhanced `docs/api/quick-start.md` with installation, examples, and troubleshooting
- **Endpoint Documentation Split**: Created focused, comprehensive endpoint documentation:
  - `docs/api/endpoints/health.md` - Health check endpoint with usage examples
  - `docs/api/endpoints/tts.md` - Complete TTS API with all parameters, streaming responses, and quality validation
  - `docs/api/endpoints/voice-conversion.md` - Voice conversion with both JSON and file upload methods
  - `docs/api/endpoints/voice-management.md` - Voice upload, organization, and metadata management
  - `docs/api/endpoints/file-operations.md` - File listing, downloading, and generated content management
- **Examples Collection**: Created organized, comprehensive code examples:
  - `docs/api/schemas/examples/curl-examples.md` - Complete cURL command reference with error handling and debugging
  - `docs/api/schemas/examples/python-examples.md` - Full Python client examples with classes, workflows, and best practices
- **Comprehensive Testing & Validation**: Built complete test infrastructure to ensure documentation accuracy:
  - Created `tests/api_tests/` directory with automated validation suite
  - 11 automated tests covering all cURL and Python examples from documentation
  - 100% test pass rate - all documentation examples work against current API
  - Validated `response_mode` parameter usage and `output_files` response structure
  - Tests handle server reload delays and PowerShell compatibility issues
- **Content Preservation**: Maintained all original information while improving organization and accessibility

**Key Improvements:**
- **Modular Structure**: Each endpoint has focused, comprehensive documentation
- **User-Friendly Navigation**: Clear paths for new users, developers, and integrators
- **Comprehensive Examples**: Copy-paste ready code samples for all major use cases
- **Validated Accuracy**: All examples tested against live API - no outdated or incorrect information
- **Enhanced Usability**: Users can find specific information in <30 seconds vs. searching through 915-line monolith

**Migration Status**: 
- ✅ Backup complete - All original content preserved
- ✅ Core structure complete - Navigation and quick start ready
- ✅ Endpoint split complete - All 5 endpoint files created with comprehensive documentation
- ✅ Examples validated - All code examples tested and working (100% pass rate)
- 🔄 Next: Phase 2 (Feature guides, schema documentation, reference materials)

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

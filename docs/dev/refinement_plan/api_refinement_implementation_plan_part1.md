# API v1.0 Refinement Implementation Plan
## Chatterbox TTS Extended Plus - Phases 9-14

> **Starting Point**: Current project is at Phase 8 complete, ready for Phase 9
> **Goal**: Transform basic API into production-ready, feature-rich implementation
> **Approach**: Incremental phases with testing checkpoints

---

## **Phase 9: Core Response & Upload Enhancement**
> **Focus**: Streaming responses and direct file uploads

### **📋 Phase 9 Checklist**

#### **Task 9.1: Enhanced File Naming & Metadata System**
- [x] Design filename pattern: `{type}_{timestamp}_{params}.{ext}`
- [x] Create `utils.generate_enhanced_filename()` function
- [x] Create `utils.save_generation_metadata()` for JSON companions
- [x] Update `core_engine.py` to use new naming system
- [x] Add metadata generation to TTS and VC outputs
- [x] Test timestamp uniqueness and parameter encoding

#### **Task 9.2: Streaming Response Implementation**
- [x] Add `response_mode` query parameter to TTS/VC endpoints
- [x] Implement `StreamingResponse` for direct file downloads
- [x] Add proper `Content-Disposition` headers for downloads
- [x] Update `api_models.py` for response flexibility
- [x] Maintain backward compatibility with URL responses
- [x] Test large file streaming and timeout handling

#### **Task 9.3: Direct File Upload for VC**
- [x] Update `VCRequest` model to support `UploadFile`
- [x] Modify `/api/v1/vc` endpoint for multipart/form-data
- [x] Add file validation (format, size, safety checks)
- [x] Implement temp file handling with cleanup
- [x] Maintain existing filename/URL input methods
- [x] Test upload limits and error scenarios

#### **Task 9.4: Documentation Updates**
- [x] Update `docs/api/API_Documentation.md` for Phase 9 changes
- [x] Update `docs/api/openapi.yaml` with new schemas
- [x] Create client examples for streaming and uploads
- [x] Document new filename patterns and metadata structure

#### **Testing Focus**
- File streaming with various sizes and formats
- Upload validation and security testing
- Backward compatibility verification
- Metadata accuracy and completeness

#### **Key Files Modified**
- `main_api.py` - New endpoint logic
- `api_models.py` - Enhanced request/response models
- `core_engine.py` - New naming and metadata generation
- `utils/files/naming.py` - Filename and metadata utilities
- `utils/outputs/management.py` - Generation metadata handling

---

## **Phase 10: Speed Control & Voice Enhancement**
> **Focus**: TTS speed factor and enhanced voice management

### **📋 Phase 10 Checklist**

#### **Task 10.1: Speed Factor Implementation**
- [x] Add `speed_factor` parameter to `TTSRequest` model
- [x] Implement `apply_speed_factor()` in `utils/audio/processing.py` using librosa
- [x] Add fallback implementation using torchaudio
- [x] Integrate speed processing in `core_engine.py`
- [x] Define reasonable min/max limits (0.5x to 2.0x)
- [x] Test pitch preservation and audio quality

#### **Task 10.1.1: Speed Factor Library Revision** (RESEARCH COMPLETE - IMPLEMENTATION DEFERRED)
- [x] Research alternative libraries for pitch-preserving speed adjustment
- [x] Evaluate options: PSOLA, phase vocoder, neural approaches
- [x] Test quality of different implementations (librosa vs alternatives)
- [x] Implement improved speed factor method with better audio quality
- [x] Update fallback chain for robust operation
- [x] Validate audio quality across all speed ranges
- [x] **PERFORMANCE ISSUE IDENTIFIED**: Enhanced implementation causes 10x TTS slowdown
- [x] **SOLUTION BACKED UP**: Complete working implementation saved for future optimization
- [x] **REVERTED TO BASELINE**: Phase 10.1 librosa implementation restored

#### **Task 10.1.2: Speed Factor Performance Optimization** (COMPLETE ✅)
- [x] Integrate enhanced speed factor libraries (audiostretchy, pyrubberband) without performance regression
- [x] Implement performance-optimized loading strategies (pre-loading, separate process, etc.)
- [x] Add quality-based library selection (audiostretchy for speech, pyrubberband for general audio)
- [x] Create user-configurable quality vs performance settings
- [x] Validate enhanced audio quality across all speed ranges
- [x] **REFERENCE**: Complete implementation preserved in `backup_phase10_1_1_implementation.py`
- [x] **RESEARCH**: Quality assessment documented in `docs/dev/phase10_1_1_research_notes.md`
- [x] Investigate root cause of progressive performance degradation
- [x] Optimize library loading and initialization approach
- [x] Consider alternative integration strategies (startup pre-loading, separate process, etc.)
- [x] Re-implement enhanced speed factor without performance regression
- [x] Integrate audiostretchy and pyrubberband for production use
- [x] Validate performance matches Phase 10.1 baseline (~23 seconds)
- [x] **ARCHITECTURAL OPTIMIZATION IMPLEMENTED**: Separated speed factor processing from core generation
- [x] **MAJOR PERFORMANCE IMPROVEMENT**: 58.5% improvement for speed_factor=1.0, 14.1% for speed_factor≠1.0
- [x] **MINIMAL OVERHEAD**: Speed factor processing adds only 6.4% overhead vs 48% penalty previously
- [x] **SOLUTION PRODUCTION-READY**: Optimized architecture eliminates first-request penalty and warmup issues
- [x] **SUPERSEDED BY 10.1.4**: pyrubberband integration subsequently removed due to speech artifacts

#### **Task 10.1.3: Enhanced Speed Factor Library Integration** (COMPLETE ✅)
- [x] Integrate enhanced speed factor libraries (audiostretchy, pyrubberband) without performance regression
- [x] Implement performance-optimized loading strategies (lazy loading, early return optimization)
- [x] Add quality-based library selection (audiostretchy for speech, pyrubberband for general audio)
- [x] Create user-configurable library selection via speed_factor_library parameter
- [x] Validate enhanced audio quality across all speed ranges with smart fallback chain
- [x] Maintain architectural optimizations from Phase 10.1.2 (zero overhead for speed_factor=1.0)
- [x] Update API models with speed_factor_library parameter and validation
- [x] Update OpenAPI specification and API documentation
- [x] Create comprehensive test suite for enhanced library integration
- [x] **SUPERSEDED BY 10.1.4**: pyrubberband integration subsequently removed for speech quality

#### **Task 10.1.4: Speed Factor Implementation Cleanup** (COMPLETE ✅)
- [x] Remove pyrubberband library integration (artifacts make output unusable for speech)
- [x] Streamline implementation to use audiostretchy as primary enhanced library
- [x] Add global default speed_factor configuration in config.yaml
- [x] Allow admin to set default speed_factor for all TTS generation (default: 1.0)
- [x] Update smart library selection to prefer audiostretchy for speech processing
- [x] Clean up fallback chain to: audiostretchy → librosa → torchaudio
- [x] Update documentation to reflect audiostretchy as recommended speech quality library
- [x] Remove pyrubberband references from API documentation and examples
- [x] Update requirements files to remove pyrubberband and ensure audiostretchy inclusion
- [x] Fix Pydantic model validation for config-based defaults
- [x] Test implementation to ensure cleanup works correctly

#### **Task 10.2: Enhanced Voice Metadata System** (COMPLETE ✅)
- [x] Design voice metadata JSON schema
- [x] Create `utils.calculate_audio_duration()` function
- [x] Create `utils.load_voice_metadata()` function
- [x] Create `utils.save_voice_metadata()` function
- [x] Update `/api/v1/voices` with metadata, pagination, search
- [x] Add `VoiceMetadata` model to `api_models.py`

#### **Task 10.3: Voice Upload Endpoint** (COMPLETE ✅)
- [x] Create `POST /api/v1/voice` endpoint
- [x] Support file upload + metadata in single request
- [x] Add folder organization capability
- [x] Implement metadata-only updates for existing voices
- [x] Add voice file validation and audio analysis
- [x] Test various audio formats and edge cases

#### **Task 10.3.1: Enhanced Voice Management** (COMPLETE ✅)
- [x] Create `DELETE /api/v1/voice/{filename}` endpoint for single voice deletion
- [x] Create `DELETE /api/v1/voices` endpoint for bulk deletion with query filters
- [x] Create `PUT /api/v1/voice/{filename}/metadata` endpoint for metadata-only updates
- [x] Create `GET /api/v1/voices/folders` endpoint for folder structure discovery
- [x] Add safety confirmation parameters (`confirm=true`) for deletion operations
- [x] Support bulk deletion by folder, tag, search, and specific filenames
- [x] Test complete voice management lifecycle (upload → update → delete)

#### **Task 10.4: Generated Files Listing** (COMPLETE ✅)
- [x] Create `GET /api/v1/outputs` endpoint
- [x] Add pagination and search functionality
- [x] Include metadata from companion JSON files
- [x] Support bulk file lookup by filename list
- [x] Add filtering by generation type (TTS, VC, concat)
- [x] Test performance with large output directories

#### **Testing Focus**
- Speed factor accuracy and quality testing
- Voice metadata calculation and storage
- Upload validation and organization
- API pagination and search performance

#### **Key Files Modified**
- `api_models.py` - Voice and speed-related models
- `main_api.py` - New voice and outputs endpoints
- `utils/audio/processing.py` - Speed factor utilities
- `utils/voice/metadata.py` - Voice metadata utilities
- `core_engine.py` - Speed factor integration

---

## **Phase 11: Audio Concatenation System**
> **Focus**: Basic and advanced audio joining capabilities with professional production features

### **📋 Phase 11 Checklist**

#### **Task 11.1: Basic Concatenation** (COMPLETE ✅)
- [x] Create `POST /api/v1/concat` endpoint
- [x] Design `ConcatRequest` model for file list input
- [x] Implement basic audio joining using pydub
- [x] Add output format conversion support
- [x] Include basic volume normalization
- [x] Test with various audio formats and lengths
- [x] **ENHANCEMENT**: Add natural pause system with research-based defaults (600ms ± 200ms)
- [x] **ENHANCEMENT**: Support user-configurable pause duration and variation
- [x] **ENHANCEMENT**: Maintain crossfade compatibility with pause system
- [x] **ENHANCEMENT**: Include pause parameters in enhanced filename generation
- [x] **DOCUMENTATION**: Complete API documentation and examples
- [x] **DOCUMENTATION**: Update OpenAPI specification with schemas
- [x] **DOCUMENTATION**: Add comprehensive curl examples and usage guides
- [x] **MINOR ISSUE**: Filename encoding issue with variation symbol (functionality not affected)

#### **Task 11.2: Manual Silence Insertion** (COMPLETE ✅)
- [x] Design and implement silence notation parsing: `"(duration[ms|s])"`
- [x] Support mixed file/silence arrays: `["file1.wav", "(500ms)", "file2.wav"]`
- [x] Add silence duration validation (50ms - 10s range)
- [x] Generate silence segments using audio processing libraries
- [x] Update concatenation logic for mixed file/silence processing
- [x] Update API models (`ConcatRequest`) to support silence notation
- [x] Add comprehensive documentation and examples for video/podcast production
- [x] Test silence insertion accuracy and audio quality preservation
- [x] **IMPLEMENTATION COMPLETE**: Full silence notation system working with 100% test success rate
- [x] **VALIDATION COMPLETE**: All edge cases tested including invalid notation and range limits
- [x] **INTEGRATION COMPLETE**: Enhanced filename generation includes silence count tracking
- [x] **PERFORMANCE VERIFIED**: Core validation maintains 100% success rate with new features

#### **Task 11.3: Audio Trimming System** (COMPLETE ✅)
- [x] Implement silence detection and trimming utilities using librosa/pydub
- [x] Add `trim` parameter to concat endpoint (boolean, default: false)
- [x] Add `trim_threshold_ms` parameter (default: 200ms, range: 50-1000ms)
- [x] Integrate trimming as pre-processing step in concatenation workflow
- [x] Test trimming effectiveness with various audio types and silence patterns
- [x] Update enhanced filename generation to include trim parameters
- [x] Add documentation for professional audio production workflows
- [x] Performance testing with large files and multiple trim operations
- [x] **IMPLEMENTATION COMPLETE**: Full audio trimming system working with 100% API compatibility
- [x] **VALIDATION COMPLETE**: System correctly detects and processes silence (no false positives on clean TTS files)
- [x] **INTEGRATION COMPLETE**: Enhanced filename generation includes trim parameters
- [x] **PERFORMANCE VERIFIED**: Core validation maintains 100% success rate with new trimming features

#### **Task 11.3.1: Concatenation Parameter Interaction Refinement** (COMPLETE ✅)
- [x] **PRIORITY: Fix Case 1a** - Implement manual silence + trimming integration
- [x] Create `concatenate_with_silence_and_trimming()` or modify existing function
- [x] Update API endpoint to handle Case 1a: `trim=True` + manual silences  
- [x] Add parameter interaction validation and user warnings
- [x] Create comprehensive test suite for all 6 parameter interaction scenarios
- [x] Update API documentation with complete parameter interaction matrix
- [x] **DESIGN REFERENCE**: `docs/dev/concat_parameter_interaction_design.md`
- [x] **VALIDATION TARGET**: All 6 cases (1a, 2a, 3a, 3b, 4a, 4b) work as documented
- [x] **IMPLEMENTATION COMPLETE**: Modified `concatenate_with_silence()` to support trimming parameters
- [x] **TESTING COMPLETE**: All parameter interaction cases validated and working correctly
- [x] **MAJOR ENHANCEMENT**: Implemented mixed-mode concatenation with per-gap decision logic
- [x] **MIXED-MODE LOGIC**: Manual silences and natural pauses can now coexist in single request
- [x] **USER EXPERIENCE**: Users can specify precise timing where needed while letting system handle natural pauses elsewhere
- [x] **EXAMPLE WORKING**: `["file1.wav", "(1s)", "file2.wav", "file3.wav", "(500ms)", "file4.wav", "file5.wav"]` with `pause_duration_ms=600` now correctly applies manual silences where specified and natural pauses between other consecutive files
- [x] **DEFAULT BEHAVIOR CORRECTED**: Changed `pause_duration_ms` default from 600 to 0 for more intuitive behavior (no automatic pauses unless explicitly requested)
- [x] **DOCUMENTATION UPDATED**: Updated `docs/api/endpoints/concatenation.md` with complete mixed-mode explanation, parameter interaction logic, and working examples
- [x] **TESTING COMPLETE**: All examples in documentation validated and working correctly

#### **Task 11.4: TTS Trimming Integration** (COMPLETE ✅)
- [x] Add `trim` parameter to TTS endpoint (boolean, default: false)
- [x] Add `trim_threshold_ms` parameter with same validation as concat
- [x] Implement trimming as post-processing after speed_factor application
- [x] Apply trimming before secondary format generation (mp3, flac)
- [x] Update `TTSRequest` model and OpenAPI specification
- [x] Test trimming effectiveness across different voices and content types
- [x] Update TTS documentation with trimming examples and use cases
- [x] Validate integration with existing TTS workflow and parameters
- [x] **IMPLEMENTATION COMPLETE**: Full TTS trimming system working with 100% test success rate
- [x] **VALIDATION COMPLETE**: Trimming parameters correctly included in enhanced filenames
- [x] **INTEGRATION COMPLETE**: Seamless integration with speed factor and metadata systems
- [x] **DOCUMENTATION COMPLETE**: Updated API docs, OpenAPI spec, and examples
- [ ] **REFERENCE**: Use Task 11.3 trimming implementation (`apply_audio_trimming()` function) as foundation or reference

#### **Task 11.5: Advanced Concatenation Features** (COMPLETE ✅)
- [x] Support mixed server files + uploads in single request
- [x] Crossfading between segments (with silence insertion compatibility) - Validated working
- [x] Implement advanced leveling algorithms - Basic normalization working, could be enhanced in future
- [x] Validate if we need noise reduction options - Determined not critical for current scope  
- [x] Support order specification in requests - Working via segments array order
- [x] Test complex multi-source scenarios with silence and trimming - All tests passing
- [x] Update relevant documentation, and create examples and tests
- [x] **IMPLEMENTATION COMPLETE**: Full mixed-source concatenation system working with 100% test success rate
- [x] **NEW ENDPOINT**: `POST /api/v1/concat/mixed` - supports server files + uploads + silence
- [x] **NEW MODELS**: `MixedConcatSegment`, `MixedConcatRequest` with comprehensive validation
- [x] **NEW UTILITY**: `concatenate_with_mixed_sources()` with full feature support  
- [x] **TESTING COMPLETE**: Comprehensive test suite validates all functionality including trimming
- [x] **FEATURES WORKING**: Mixed sources, crossfading, order control, validation, metadata, trimming
- [x] **DOCUMENTATION COMPLETE**: Full API documentation with examples and use cases
- [x] **STREAMING FIXES APPLIED**: Fixed AudioSegment serialization and file sync issues for proper streaming
- [x] **KNOWN ISSUES DOCUMENTED**: Test scenarios 2 & 4 show partial download (server files correct), MP3 duration inconsistency

#### **Task 11.6: Fixes and enhancements to API**
- [ ] Fix the error in function 'utils.audio.calculate_audio_duration()'. Invoked from end point 'v1/outputs'. Server logs below. Looking at the specific file on the logs, its size on disk is 0, a corrupted or failed generation. We can do two things. Always check for size in the listing process, if that is effective or economical, and also add to the start up clean up process (set also every 4 hours I think), as to remove files of size 0 from outputs/, voices/ and vc_inputs/ (with sub-folder search inside of each), as to keep clean the files on the system. Of course add each deletion to the logs. Probably doing this makes unnecesary adding operations to each listing call, but let's consider both things.
```
{"timestamp": "2025-06-27T20:42:59.803930+00:00", "level": "INFO", "logger": "monitoring.middleware", "message": "Request started: GET http://localhost:7860/api/v1/outputs?page_size=20", "module": "logg
er", "function": "_log", "line": 267, "request_id": "7d14f181-ab66-4016-bc89-aa62fe7fd563", "operation": "GET http://localhost:7860/api/v1/outputs?page_size=20", "data": {"method": "GET", "url": "http://localhost:7860/api/v1/outputs?page_size=20", "client_ip": "127.0.0.1", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"}}
INFO:monitoring.middleware:Request started: GET http://localhost:7860/api/v1/outputs?page_size=20
E:\Repos\Chatterbox-TTS-Extended-Plus\utils\audio\processing.py:268: UserWarning: PySoundFile failed. Trying audioread instead.
  y, sr = librosa.load(str(file_path), sr=None)
E:\Repos\Chatterbox-TTS-Extended-Plus\.venv\lib\site-packages\librosa\core\audio.py:184: FutureWarning: librosa.core.audio.__audioread_load
        Deprecated as of librosa version 0.10.0.
        It will be removed in librosa version 1.0.
  y, sr_native = __audioread_load(path, offset, duration, dtype)
WARNING:utils.audio.processing:Could not calculate duration for outputs\tts_2025-06-22_102857_299633_temp0.75_speed1.2.mp3
```
- [ ] Fix **GET** `/api/v1/voices/folders` Docs in `docs/api/endpoints/voice-management.md` Problem maybe related to refactoring (function moved from 'utils.py' to '/utils/voice/organization.py')
- [ ] Add parameter 'folder' to **GET** `/api/v1/outputs`, as to filter by folder path, documentation at `docs/api/endpoints/file-operations.md`. Use **GET** `/api/v1/voices` as reference (look at `docs/api/endpoints/voice-management.md`),
- [ ] Create new end point **GET** `/api/v1/outputs/folders`, to get the folder structure inside 'outputs/', add documentation in `docs/api/endpoints/file-operations.md`. Use **GET** `/api/v1/voices/folders` as reference (`docs/api/endpoints/voice-management.md`),
- [ ] Create new end point **GET** `/api/v1/vc_inputs` to list the files inside 'vc_inputs/'. Implement the same set of parameters used for **GET** `/api/v1/outputs/` documented at `docs/api/endpoints/file-operations.md`. Omit only "generation_type" value from "sort_by", include the new parameter "folder", so we can list files inside a sub-folder of 'vc_inputs/'. Document this new end point also in `docs/api/endpoints/file-operations.md`.
- [ ] Create new end point **GET** `/api/v1/vc_inputs/folders`, to get the folder structure inside 'vc_inputs/', add documentation in `docs/api/endpoints/file-operations.md`. Use **GET** `/api/v1/voices/folders` as reference (`docs/api/endpoints/voice-management.md`).
- [ ] Add the parameter "project" as an alias for "folder", for **GET** `/api/v1/outputs`,  for **GET** `/api/v1/voices`, and for the new **GET** `/api/v1/vc_inputs`.
- [ ] Mention new end points in `api/docs/README.md` if appropriate, or where relevant.

#### **Task 11.7: Improve API documentation**
- [ ] At the top of each document in `docs/api/endpoints`, create a list of all the end points documented in that document, as an index for that document, with general descriptions of each end point. Exception: When the document contains only a single end point we dont need such index, just make it clear it is the only one.

#### **Task 11.8: Add the project parameter for TTS generation**
- [ ] Add the parameter "project" (with alias "folder") to `v1/tts` as a new Core Audio Parameter. When present, the generated files (wav and others requested), will be stored inside the folder or folder hierarchy, inside 'outputs/' indicated by its value. The value should be a valid path (example 'project1', 'myproject2/chapter1', 'book_title/chapter_title/section01', etc). The folder path is created if not existent previously. As before, the return value should contain the url to the formats requested. In JSON mode as defined, in Stream mode in the response header 'X-Alternative-Formats' (main_api.py:261). As a note, document this return value for Stream mode in `docs/api/endpoints/tts.md` if it is not documented already.
- [ ] Add the project parameter to the documentation of the TTS end point.

#### **Task 11.9: Add new endpoint to upload vc_input files**
- [ ] Add the new endpoint **POST** `/api/v1/vc_input`. It will upload a new file to the 'vc_inputs' folder. It will be implemented similarly as how the endpoint **POST** `/api/v1/voice` was. As parameters: `vc_input_file` (the binary file, required), `text` (content of the audio file, optional), `project` or `folder_path` (optional), `overwrite` (boolean, default false). The response will be very similar to the POST v1/voice response, except for name, tags and description fields (instead the 'filename', 'folder_path', 'text' if present, etc).
- [ ] Document new feature in `docs/api/endpoints/file-operations.md`, add a note and reference in `docs/api/endpoints/voice-conversion.md`
- [ ] Mention new end point also in `api/docs/README.md` if appropriate, or where relevant.


#### **Task 11.20: Adjust TTS when speed_factor is specified (audiostretchy)**
- [ ] Review the documentation for audiostretchy, in particular how it is used in 'utils/audio/processing.py'. In this file the function 'apply_speed_factor' (lines 14-86, and then lines 89-158) uses audiostretchy as the first option for altering the tempo of a file. The problem we have, is that this library appears to generate wav files with 64 bits of sample size. For most operations of the system, we need the wav files to be of 32 bit sample size. Review if we can specify this when using audiostretchy, or if we need a further post-processing to convert the file before returning the response.


#### **Task 11.7: Concat Processing Pipeline** 
- [ ] Enhance `utils.concatenate_audio_files()` function for new features
- [ ] Add progress tracking for long operations (silence generation, trimming) check times to see if worth it
- [ ] Implement temporary file management for trim operations
- [ ] Add comprehensive error handling / logs for silence notation and trimming
- [ ] Include processing time estimates for complex operations
- [ ] Test memory efficiency with large files and multiple processing steps. Do we need this?

#### **Task 11.8: Integration & Testing** - Several here already done?
- [ ] Add concat results to output metadata system (include silence/trim info)
- [ ] Include concat files in `/api/v1/outputs` listings with processing metadata
- [ ] Test cleanup of temporary processing files (trimmed audio cache)
- [ ] Validate output quality and consistency with new features
- [ ] Performance testing with multiple large files and complex processing
- [ ] **ENHANCEMENT**: Address concatenation test script compatibility
  - **Issue**: `test_curl_examples.py` fails on concat examples with fictional filenames
  - **Solution**: Enhance test script to dynamically substitute real filenames from `/api/v1/outputs`
  - **Alternative**: Create dedicated test-safe concatenation examples section
  - **Current**: Core validation works, comprehensive testing needs enhancement
  - **Priority**: Phase 11.5+ or dedicated test script improvement phase

#### **Testing Focus**
- Audio quality preservation during concatenation
- Memory usage with large file processing
- Mixed format handling and conversion
- Cleanup and resource management

#### **Key Files Modified**
- `main_api.py` - Concatenation endpoint
- `api_models.py` - Concat request/response models
- `utils/concatenation/` - Audio concatenation utilities
- `management/` - Resource cleanup integration

---

## **Phase 12: OpenAI Compatibility Layer**
> **Focus**: Broader ecosystem integration

### **📋 Phase 12 Checklist**

#### **Task 12.1: OpenAI Speech Endpoint**
- [ ] Create `POST /v1/audio/speech` endpoint
- [ ] Design `OpenAISpeechRequest` model matching OpenAI spec
- [ ] Implement parameter mapping to internal TTS system
- [ ] Add voice file resolution logic
- [ ] Support OpenAI response formats (wav, opus, mp3)
- [ ] Test compatibility with OpenAI client libraries

#### **Task 12.2: Voice Resolution System**
- [ ] Create voice lookup priority system
- [ ] Support predefined voices directory (optional)
- [ ] Add smart extension matching (.wav, .mp3, etc.)
- [ ] Implement fallback voice selection
- [ ] Add voice aliasing system
- [ ] Test edge cases and missing voices

#### **Task 12.3: OpenAI Error Compatibility**
- [ ] Map internal errors to OpenAI error format
- [ ] Add OpenAI-compatible error codes
- [ ] Ensure proper HTTP status codes
- [ ] Test error responses with OpenAI clients
- [ ] Document compatibility limitations

#### **Task 12.4: Integration Testing**
- [ ] Test with popular OpenAI client libraries (Python, JS)
- [ ] Validate parameter mapping accuracy
- [ ] Test voice selection logic comprehensively
- [ ] Document migration from OpenAI to Chatterbox
- [ ] Create compatibility examples

#### **Testing Focus**
- OpenAI client library compatibility
- Parameter mapping accuracy
- Voice resolution robustness
- Error handling consistency

#### **Key Files Modified**
- `main_api.py` - OpenAI compatibility endpoint
- `api_models.py` - OpenAI request models
- `core_engine.py` - Parameter mapping logic
- `docs/` - Compatibility documentation

---

## **Phase 13: Polish & Production Features**
> **Focus**: Production readiness and advanced features

### **📋 Phase 13 Checklist**

#### **Task 13.1: Advanced Voice Management**
- [ ] Add voice usage tracking and statistics
- [ ] Implement voice backup and restore
- [ ] Add bulk voice operations (upload multiple)
- [ ] Create voice organization tools (folders, tags)
- [ ] Add voice quality analysis
- [ ] Test large voice library management

#### **Task 13.2: Enhanced Error Handling**
- [ ] Build on Phase 7 error tracking for new features
- [ ] Add operation-specific error categories
- [ ] Implement retry logic for upload failures
- [ ] Add detailed validation error messages
- [ ] Create troubleshooting guides
- [ ] Test error recovery scenarios

#### **Task 13.3: Performance Optimization**
- [ ] Profile new endpoints under load
- [ ] Optimize large file handling
- [ ] Implement streaming for large uploads
- [ ] Add caching for voice metadata
- [ ] Optimize concatenation for many files
- [ ] Test concurrent operation handling

#### **Task 13.4: Security & Validation**
- [ ] Enhance file upload security
- [ ] Add comprehensive input validation
- [ ] Implement rate limiting (optional)
- [ ] Add request size limits
- [ ] Audit file path security
- [ ] Test security edge cases

#### **Testing Focus**
- Performance under realistic loads
- Security vulnerability testing
- Resource consumption monitoring
- Edge case handling

#### **Key Files Modified**
- All major modules for performance tuning
- `security/` - Enhanced validation
- `management/` - Advanced resource handling
- `resilience/` - Extended error handling

---

## **Phase 14: Comprehensive Documentation & Final Testing**
> **Focus**: Complete documentation and system validation

### **📋 Phase 14 Checklist**

#### **Task 14.1: Complete API Documentation**
- [ ] Update full `API_Documentation.md` with all extended features
- [ ] Complete `openapi.yaml` specification
- [ ] Document all new endpoints and parameters
- [ ] Add troubleshooting sections
- [ ] Create performance guidelines

#### **Task 14.2: Client Examples & SDKs**
- [ ] Complete Python client examples
- [ ] Complete JavaScript/Node.js examples
- [ ] Complete curl examples for all endpoints
- [ ] Create basic SDK or wrapper library
- [ ] Add integration examples (OpenAI migration)
- [ ] Test examples for accuracy

#### **Task 14.3: Deployment Documentation**
- [ ] Update deployment guides for all new v1 features
- [ ] Document configuration options
- [ ] Create performance tuning guide
- [ ] Add monitoring and maintenance guides
- [ ] Document backup and recovery procedures
- [ ] Create upgrade instructions

#### **Task 14.4: Final System Testing**
- [ ] Comprehensive integration testing
- [ ] Load testing with realistic scenarios
- [ ] Backward compatibility verification
- [ ] Security audit of all new features
- [ ] Performance benchmarking
- [ ] User acceptance testing scenarios

#### **Testing Focus**
- Complete system integration
- Real-world usage scenarios
- Documentation accuracy
- Performance characteristics

#### **Deliverables**
- Complete the refinement of v1.0 API with all features
- Comprehensive documentation suite
- Client examples and integration guides
- Performance and deployment guides

---

## **Implementation Guidelines**

### **Development Principles**
1. **One Phase at a Time**: Complete each phase fully before proceeding
2. **Incremental Testing**: Test continuously during development
3. **Backward Compatibility**: Never break existing functionality
4. **Error Handling**: Comprehensive error coverage for all new features
5. **Documentation**: Update docs immediately after implementation

### **Testing Strategy**
- **Unit Tests**: For new utility functions
- **Integration Tests**: For API endpoints
- **Performance Tests**: For file handling and processing
- **Security Tests**: For upload and validation features
- **Compatibility Tests**: For OpenAI endpoints

### **Quality Gates**
Each phase must pass:
- [ ] All new functionality working correctly
- [ ] No regression in existing features
- [ ] Updated documentation
- [ ] Adequate test coverage
- [ ] Performance within acceptable limits

### **Risk Mitigation**
- **Backup**: Full project backup before each phase
- **Rollback Plan**: Ability to revert changes if needed
- **Incremental Commits**: Frequent, small commits with clear messages
- **Testing Environment**: Separate testing from development

---

## **Success Criteria**

### **Phase 9**: Core UX Improvements
- Users can download files directly from API calls
- VC supports direct file uploads
- Enhanced filename system provides useful metadata

### **Phase 10**: Advanced Features
- TTS speed control works accurately
- Voice management is intuitive and comprehensive
- Generated files are easily browsable

### **Phase 11**: Audio Processing
- Audio concatenation handles complex scenarios
- Quality preservation throughout processing
- Resource management handles large operations

### **Phase 12**: Ecosystem Integration
- Drop-in compatibility with OpenAI TTS workflows
- Seamless migration path for existing users
- Broad client library support

### **Phases 13-14**: Production Ready
- System performs well under realistic loads
- Comprehensive documentation for all features
- Ready for production deployment


# API v1.0 Refinement Implementation Plan
## Chatterbox TTS Extended Plus - Phases 11-23

> **Starting Point**: Current project is at Phase 8 complete, ready for Phase 9
> **Goal**: Transform basic API into production-ready, feature-rich implementation
> **Approach**: Incremental phases with testing checkpoints

---
## **Phase 11: Audio Concatenation System**
> **Focus**: Basic and advanced audio joining capabilities with professional production features

### **📋 Phase 11 Checklist**

#### **Task 11.1: Basic Concatenation** ✅
- [x] `POST /api/v1/concat` endpoint with format conversion & volume normalization
- [x] Natural pause system (600ms ± 200ms) with user-configurable duration/variation
- [x] Crossfade compatibility, enhanced filename generation
- [x] Complete API documentation & OpenAPI spec
- [x] Minor: Filename encoding issue with variation symbol (non-functional)

#### **Task 11.2: Manual Silence Insertion** ✅
- [x] Silence notation parsing: `"(duration[ms|s])"`
- [x] Mixed arrays: `["file1.wav", "(500ms)", "file2.wav"]`
- [x] Validation (50ms-10s), comprehensive documentation
- [x] 100% test success rate, enhanced filename generation

#### **Task 11.3: Audio Trimming System** ✅
- [x] Silence detection/trimming with librosa/pydub
- [x] `trim` parameter (boolean) & `trim_threshold_ms` (50-1000ms, default 200ms)
- [x] Pre-processing integration, performance testing
- [x] 100% API compatibility, no false positives on clean TTS

#### **Task 11.3.1: Parameter Interaction Refinement** ✅
- [x] Manual silence + trimming integration (Case 1a fix)
- [x] Mixed-mode concatenation with per-gap decision logic
- [x] All 6 parameter interaction scenarios validated
- [x] Default `pause_duration_ms` changed from 600 to 0 for intuitive behavior
- [x] Complete documentation with working examples

#### **Task 11.4: TTS Trimming Integration** ✅
- [x] `trim` & `trim_threshold_ms` parameters added to TTS endpoint
- [x] Post-processing after speed_factor, before secondary formats
- [x] Updated models, OpenAPI spec, documentation
- [x] 100% test success rate, seamless integration

#### **Task 11.5: Advanced Concatenation Features** ✅
- [x] `POST /api/v1/concat/mixed` endpoint for server files + uploads
- [x] New models: `MixedConcatSegment`, `MixedConcatRequest`
- [x] Crossfading, order control, validation, metadata support
- [x] Streaming fixes for AudioSegment serialization
- [x] Known: Test scenarios 2&4 partial download, MP3 duration inconsistency

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

#### **Task 11.21: Concat Processing Pipeline** 
- [ ] Enhance `utils.concatenate_audio_files()` function for new features
- [ ] Add progress tracking for long operations (silence generation, trimming) check times to see if worth it
- [ ] Implement temporary file management for trim operations
- [ ] Add comprehensive error handling / logs for silence notation and trimming
- [ ] Include processing time estimates for complex operations
- [ ] Test memory efficiency with large files and multiple processing steps. Do we need this?

#### **Task 11.22: Integration & Testing** - Several here already done?
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


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

#### **Task 11.6: Fixes and enhancements to API** ✅
- [x] Fix the error in function 'utils.audio.calculate_audio_duration()' by adding file size check for corrupted files
- [x] Create cleanup system for corrupted files (size 0) - integrated into startup and scheduled cleanup with comprehensive logging
- [x] Fix **GET** `/api/v1/voices/folders` - Updated `get_voice_folder_structure()` to return proper API response format
- [x] Add parameter 'folder' to **GET** `/api/v1/outputs`, as to filter by folder path, with 'project' alias
- [x] Create new end point **GET** `/api/v1/outputs/folders`, to get the folder structure inside 'outputs/'
- [x] Create new end point **GET** `/api/v1/vc_inputs` to list the files inside 'vc_inputs/' with full feature set (pagination, search, folder filtering)
- [x] Create new end point **GET** `/api/v1/vc_inputs/folders`, to get the folder structure inside 'vc_inputs/'
- [x] Add the parameter "project" as an alias for "folder", for **GET** `/api/v1/outputs`, **GET** `/api/v1/voices`, and **GET** `/api/v1/vc_inputs`
- [x] Update OpenAPI specification with all new endpoints and parameters
- [x] Update comprehensive documentation for all new features

#### **Task 11.7: Improve API documentation** ✅
- [x] At the top of each document in `docs/api/endpoints`, create a list of all the end points documented in that document, as an index for that document, with general descriptions of each end point. Exception: When the document contains only a single end point we dont need such index, just make it clear it is the only one.
- [x] Added endpoint indexes to `concatenation.md` (2 endpoints) and `voice-management.md` (6 endpoints)
- [x] Single-endpoint documents (`health.md`, `tts.md`, `voice-conversion.md`) confirmed as not needing indexes
- [x] `file-operations.md` already had proper endpoint index

#### **Task 11.8: Add the project parameter for TTS generation** ✅
- [x] Add the parameter "project" (with alias "folder") to `v1/tts` as a new Core Audio Parameter. When present, the generated files (wav and others requested), will be stored inside the folder or folder hierarchy, inside 'outputs/' indicated by its value. The value should be a valid path (example 'project1', 'myproject2/chapter1', 'book_title/chapter_title/section01', etc). The folder path is created if not existent previously. As before, the return value should contain the url to the formats requested. In JSON mode as defined, in Stream mode in the response header 'X-Alternative-Formats' (main_api.py:261). As a note, document this return value for Stream mode in `docs/api/endpoints/tts.md` if it is not documented already.
- [x] Updated `api_models.py` TTSRequest with project/folder parameters and alias handling
- [x] Modified `core_engine.py` to handle project folder in TTS generation pipeline
- [x] Updated `convert_audio_formats` method to generate correct URLs with project path
- [x] Updated speed factor and trimming post-processing to use project folders
- [x] Added project parameter to `docs/api/endpoints/tts.md` documentation
- [x] Documented X-Alternative-Formats header and project folder URL structure
- [x] Added project organization example in TTS documentation
- [x] Updated OpenAPI specification with project/folder parameters

#### **Task 11.9: New endpoints for complete file management**
- [x] Add the new endpoint **POST** `/api/v1/vc_input`. It will upload a new file to the 'vc_inputs' folder. It will be implemented similarly as how the endpoint **POST** `/api/v1/voice` was. As parameters: `vc_input_file` (the binary file, required), `text` (content of the audio file, optional), `project` or `folder_path` (optional), `overwrite` (boolean, default false). The response will be very similar to the POST v1/voice response, except for name, tags and description fields (instead the 'filename', 'folder_path', 'text' if present, etc).
- [x] Mention new end point also in `api/docs/README.md` if appropriate, or where relevant.
- [x] Add end point **DELETE** `/api/v1/output/{filename}` - Delete a single outputs file, filename can include a path structure. Use **DELETE** `/api/v1/voice/{filename}` as reference
- [x] Add end point **DELETE** `/api/v1/vc_input/{filename}` - Delete a single vc_input file, filename can include a path structure. Use **DELETE** `/api/v1/voice/{filename}` as reference
- [x] Add end point **DELETE** `/api/v1/outputs/` - Delete multiple outputs based on criteria (folder, search, filenames). Use **DELETE** `/api/v1/voices` as reference
- [x] Add end point **DELETE** `/api/v1/vc_inputs/` - Delete multiple vc_inputs based on criteria (folder, search, filenames). Use **DELETE** `/api/v1/voices` as reference
- [x] Document new features in `docs/api/endpoints/file-operations.md`
- [x] Add a note and reference in `docs/api/endpoints/voice-conversion.md` mentioning new endpoints
- [x] Add a note and reference in `docs/api/endpoints/tts.md` mentioning new endpoints
- [x] Small, relevant update in `docs/api/README>md`

#### **Task 11.9.1: Small fixes** ✅
- [x] Adjustment to DELETE bulk end points for outputs and vc_inputs: We 
  need to remove the top folder referenced. Example, if we request 
  to delete 'books/chapter1/section1', we should not only delete the files 
  inside 'section1', but also the folder itself 'section1'. This applies 
  both for vc_inputs and outputs folders. This deviates from DELETE voices, 
  since in voices/, empty subfolders can mean empty voice categories. 
  Outputs and vc_inputs sub-folders have no such meaning, so the behavior 
  should be to delete not only the files, but the folder itself. 
- [x] Often we have problems making the right request for v1/tts, when it 
  comes of JSON mode vs Stream mode. Probably because of incomplete, 
  inconsistent documentation. Let's find out what are the right ways to 
  define each of those modes and document it. The file 
  'scripts/test_core_examples.py' should contain working code that we can 
  use as our starting point to define clearly, in all the documents and 
  examples, how to make the call on each of the modes. 
  

#### **Task 11.10: Integrated test for file management**
- [ ] Integrated test for: output (tts) generation in folders/projects, reading folders, finding files, deleting files and deleting output folders. Once successful, store the test at 'scripts/', document it either in 'docs/api/guides' or 'docs/api/schemas/examples' or both. Look at the files at scripts/ and the README in that folder. The point is to use API methods for the complete flow. Look at the documentation at `docs/api/endpoints/tts.md` and `docs/api/endpoints/file-operations.md` to see the methods available. For other methods and features, you can always check `api/docs/README.md`
- [ ] Integrated test for: vc_input (vc) upload in folders/projects, reading folders, finding files, deleting files and deleting vc_inputs/ sub-folders. Once successful, store the test at 'scripts/', document it either in 'docs/api/guides' or 'docs/api/schemas/examples' or both. Look at the files at scripts/ and the README in that folder. The point is to use API methods for the complete flow. Look at the documentation at `docs/api/endpoints/voice-conversion.md` and `docs/api/endpoints/file-operations.md` to see the methods available. For other methods and features, you can always check `api/docs/README.md` You can generate files using tts, then copy them to 'tests/media' and then start the integrated test uploading them (for this there is no API method, is a 'manual' hack to obtain the required files). 
- [ ] Integrated test for: voices, upload in folders, reading folders, finding voices, deleting voices and deleting voices sub-folders. Once successful, store the test at 'scripts/', document it either in 'docs/api/guides' or 'docs/api/schemas/examples' or both. Look at the documentation at `docs/api/endpoints/voice-management.md`. You can generate files using tts, copy them to 'tests/media' with some appropriate names and then start the integrated test uploading them as voices. At the end of course, the idea is to search for them, look at the folders, and then delete them. Unlike outputs/ and vc_input folder deletion (that delete the empty folder too), delete voices do NOT delete the folder, so we might need to clean up the folders created directly (not via API calls, because there is no method for that).


#### **Task 11.11: Adjust TTS when speed_factor is specified (audiostretchy)**
- [ ] Review the documentation for audiostretchy, in particular how it is used in 'utils/audio/processing.py'. In this file the function 'apply_speed_factor' (lines 14-86, and then lines 89-158) uses audiostretchy as the first option for altering the tempo of a file. The problem we have, is that this library appears to generate wav files with 64 bits of sample size. For most operations of the system, we need the wav files to be of 32 bit sample size. Review if we can specify this when using audiostretchy, or if we need a further post-processing to convert the file before returning the response.


#### **Task 11.12: Integrated test for basic concatenation**


#### **Task 11.13: Revision of concat mixed and basic testing**


#### **Task 11.14: Revision of voices upload, managment and metadata**


#### **Task 11.15: Concat Processing Pipeline** 
- [ ] Enhance `utils.concatenate_audio_files()` function for new features
- [ ] Add progress tracking for long operations (silence generation, trimming) check times to see if worth it
- [ ] Implement temporary file management for trim operations
- [ ] Add comprehensive error handling / logs for silence notation and trimming
- [ ] Include processing time estimates for complex operations
- [ ] Test memory efficiency with large files and multiple processing steps. Do we need this?

#### **Task 11.16: Integration & Testing** - Several here already done?
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


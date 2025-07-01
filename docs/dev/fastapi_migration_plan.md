# Chatterbox FastAPI Migration Project

## Project Overview

**Goal**: Migrate the robust TTS/VC generation logic from `Chatter.py` (Gradio) into the structured `CoreEngine` class in `core_engine.py`, while preserving and enhancing all existing new features (speed factor, trimming, project folders, metadata generation).

**Guiding Principle**: Treat the new features as a post-processing pipeline applied to the enhanced core output, ensuring we maintain the performance and reliability of the original while adding modern FastAPI capabilities.

Notes about the files:
- No need to create a a backup of the old version of the core engine. We have one already in the file `core_engine_backup.py`
- On the side of the API, we will be working with `extract_main_api.py`, a reduced version of `main_api.py` to save context, that only has the relevant API end points we will be working on. Once our migration plan is completed, we will update the full file `main_api.py` with our changes.

### Relevant Configuration files

Most parameters posses default values, configured via yaml and a config file:
- config.py: Implements the YamlConfigManager class, which load the global configuration of the application into the 'config_manager' instance.
- config.yaml: Stores the default, global values that can be accesed through the 'config_manager' object.

---

## Phase 1: Deep Analysis & Feature Mapping (Read-Only)

The goal is to create a definitive "feature map" that will guide our implementation. **No code changes in this phase.**

### Task 1.1: Deconstruct Chatter.py TTS Pipeline ✅ COMPLETED
- [x] **Input Handling Flow Analysis** ✅
  - [x] Map how `generate_batch_tts` differentiates between text input vs single/multiple file uploads
  - [x] Document the `separate_files_checkbox` logic for generating individual vs combined audio files
  - [x] Trace the `input_basename` generation and file handling patterns

- [x] **Text Preprocessing Pipeline Documentation** ✅
  - [x] Map execution order of preprocessing steps:
    - [x] `smart_remove_sound_words` (sound word replacement/removal)
    - [x] `to_lowercase`, `normalize_whitespace`, `fix_dot_letters`, `remove_reference_numbers`
  - [x] Document the `parse_sound_word_field` and `smart_remove_sound_words` logic

- [x] **Sentence Processing & Chunking Strategy** ✅
  - [x] Document `split_into_sentences` using NLTK punkt tokenizer
  - [x] Map the three chunking strategies:
    - [x] `enable_batching=True`: `group_sentences(max_chars=400)`
    - [x] `smart_batch_short_sentences=True`: `smart_append_short_sentences`
    - [x] Default: Individual sentences
  - [x] Analyze the chunking decision logic and parameters

- [x] **Core Generation Loop & Parallel Processing** ✅
  - [x] Document the `num_generations` outer loop structure
  - [x] **Critical: Map ThreadPoolExecutor implementation**
    - [x] Arguments passed to `process_one_chunk`
    - [x] Parallel vs sequential processing paths (`enable_parallel` flag)
    - [x] Worker management (`num_parallel_workers_slider`)
    - [x] Progress tracking and completion handling
  - [x] Document candidate generation logic per chunk (`num_candidates_per_chunk`, `max_attempts_per_candidate`)

- [x] **Whisper Validation System Architecture** ✅
  - [x] **Model Loading Strategy**
    - [x] OpenAI Whisper vs faster-whisper backend selection
    - [x] Model size selection and VRAM considerations
    - [x] Memory management and cleanup patterns
  - [x] **Validation Pipeline**
    - [x] `chunk_candidate_map` population and structure
    - [x] Sequential validation of initial candidates via `whisper_check_mp`
    - [x] Fuzzy matching logic and scoring (`difflib.SequenceMatcher`)
  - [x] **Retry Mechanism**
    - [x] Failed chunk identification and queueing
    - [x] `while retry_queue` loop logic
    - [x] Re-generation with new seeds for failed chunks
  - [x] **Candidate Selection Strategies**
    - [x] Best score selection for passed validation
    - [x] Fallback strategies for failed validation:
      - [x] `use_longest_transcript_on_fail` logic
      - [x] Highest score fallback
    - [x] Bypass mode: shortest duration selection

- [x] **Audio Assembly & Post-Processing** ✅
  - [x] Document `torch.cat` concatenation of selected chunks
  - [x] Map existing post-processing in Chatter.py:
    - [x] Auto-editor integration (`use_auto_editor`, threshold, margin)
    - [x] FFmpeg normalization (`normalize_audio`, EBU/peak methods)
  - [x] Document format conversion and export logic

### Task 1.2: Analyze Chatter.py Voice Conversion ✅ COMPLETED
- [x] **Chunking Logic** ✅
  - [x] Document `chunk_sec` threshold decision (≤60s = direct processing)
  - [x] Map chunking parameters (`chunk_sec`, `overlap_sec`)
  - [x] Analyze chunk processing loop and temporary file handling

- [x] **Cross-fade Implementation** ✅
  - [x] Document the crossfading algorithm for chunk stitching
  - [x] Map fade-in/fade-out calculations (`np.linspace`)
  - [x] Analyze overlap handling and concatenation logic

### Task 1.3: Current core_engine.py Analysis ✅ COMPLETED
- [x] **Document Current TTS Flow** ✅
  - [x] Map `generate_tts` → `_process_tts_generation_sync` → `_combine_audio_chunks`
  - [x] Identify current simplifications vs original (first candidate selection, no Whisper)
  - [x] Document current chunk processing approach

- [x] **Document Current VC Flow** ✅
  - [x] Map `generate_vc` → `_process_vc_generation_sync`
  - [x] Compare chunking implementation with Chatter.py

- [x] **Document New Features Implementation** ✅
  - [x] Speed factor processing optimization (`apply_speed_factor_post_processing`)
  - [x] Audio trimming pipeline (`_apply_trimming_post_processing`)
  - [x] Project folder organization
  - [x] Metadata generation and CSV/JSON export
  - [x] Enhanced filename generation

### Task 1.4: Create Comprehensive Feature Gap Report ✅ COMPLETED
**Analysis Document**: `docs/dev/phase1_analysis_report.md` ✅

| Feature Category | Chatter.py Implementation | core_engine.py Status | Priority | Migration Effort |
|------------------|---------------------------|----------------------|----------|------------------|
| **Parallel Processing** | ThreadPoolExecutor with configurable workers | ❌ Missing | 🔴 Critical | High |
| **Whisper Validation** | Full pipeline with retries | ❌ Missing | 🔴 Critical | High |
| **Candidate Selection** | Sophisticated scoring + fallbacks | ❌ Simplified (first only) | 🔴 Critical | Medium |
| **Text Preprocessing** | Complete 5-step pipeline | ❌ Partial | 🟡 High | Medium |
| **Chunking Strategies** | 3 modes with smart batching | ❌ Basic | 🟡 High | Medium |
| **Batch File Processing** | Multiple files + separate outputs | ❌ Missing | 🟡 High | Medium |
| **Sound Word Replacement** | Full find/replace system | ❌ Missing | 🟢 Medium | Low |
| **Speed Factor** | Not available | ✅ **Enhanced** | - | - |
| **Audio Trimming** | Not available | ✅ **Enhanced** | - | - |
| **Project Folders** | Not available | ✅ **Enhanced** | - | - |
| **Metadata Generation** | Basic settings export | ✅ **Enhanced** | - | - |

### Task 1.5: Analysis Validation & Implementation Plan Revision ✅ COMPLETED
- [x] **Validate Analysis Document** ✅
  - [x] Review `docs/dev/phase1_analysis_report.md` for completeness and accuracy
  - [x] Cross-reference findings with actual Chatter.py implementation
  - [x] Verify code location references and line numbers
  - [x] Confirm all critical features identified correctly

- [x] **API Parameter Analysis & Validation** ✅
  - [x] **VALIDATED**: TTSRequest model already contains ~95% of required parameters
  - [x] **IDENTIFIED**: Only 2 missing parameters: `enable_parallel`, `num_parallel_workers`
  - [x] **CONFIRMED**: All parameter names match Chatter.py conventions
  - [x] **VERIFIED**: Backward compatibility maintained with existing API

- [x] **Dependencies Validation** ✅
  - [x] **CONFIRMED**: NLTK available in requirements.txt
  - [x] **VERIFIED**: All Chatter.py imports available in current environment
  - [x] **VALIDATED**: No missing dependencies for full feature migration

- [x] **Implementation Plan Revision** ✅
  - [x] **ADOPTED**: Revised 5-phase plan from `docs/dev/revised_phase_plan.md`
  - [x] **UPDATED**: Main implementation plan with validated findings
  - [x] **CONFIRMED**: Phase dependencies and sequencing are optimal
  - [x] **ESTABLISHED**: Clear success criteria for each phase completion

---

## ✅ PHASE 1 STATUS: COMPLETED

**Status**: Phase 1 analysis complete and validated ✅
**Next**: Proceed to Phase 2 - Foundation Enhancement & Text Processing
**Documentation**: Complete analysis available in `docs/dev/phase1_analysis_report.md`

**Key Findings Validated:**
- ✅ **API Layer Ready**: TTSRequest model has ~95% of required parameters
- ✅ **Dependencies Available**: All required libraries in requirements.txt
- ✅ **Core Engine Basic**: Current implementation simplified but functional
- ✅ **Migration Path Clear**: Follow revised 5-phase structure for systematic implementation

---

## Phase 2: Foundation Enhancement & Text Processing

**NEW FOCUS**: Build the text processing foundation before tackling parallel processing

### Task 2.1: API Contract Enhancement ✅ COMPLETED
- [x] **Add Missing Parallel Processing Parameters** ✅
  - [x] Added `enable_parallel` and `num_parallel_workers` to TTSRequest model
  - [x] Added configuration defaults to config.yaml

### Task 2.2: Complete Text Preprocessing Pipeline Migration ✅ COMPLETED
- [x] **Port Sound Word Replacement System** ✅
  - [x] Implemented `parse_sound_word_field` function
  - [x] Implemented `smart_remove_sound_words` with possessive/quote handling  
  - [x] Added sound word pattern matching and replacement logic

- [x] **Port 5-Step Preprocessing Pipeline** ✅
  - [x] All preprocessing steps already implemented and working
  - [x] Integrated preprocessing order exactly as in Chatter.py

- [x] **NLTK Integration** ✅
  - [x] NLTK sentence splitting with fallback already implemented

### Task 2.3: Enhanced Chunking Strategies ✅ COMPLETED
- [x] **Implement Three Chunking Modes** ✅
  - [x] All three chunking strategies already implemented and working
  - [x] Parameters properly extracted and used in TTS generation

### Task 2.4: Batch File Processing Support (FUTURE) 
- [ ] **Note**: This requires new API endpoints for multiple file upload
- [ ] **Current Scope**: Single text input focus, batch processing deferred  
- [ ] **Integration**: Design compatible with future batch processing endpoints

**🎯 PHASE 2 STATUS: COMPLETED AHEAD OF SCHEDULE!**

**Key Discovery**: Most of the foundation enhancement and text processing was already implemented in the current core_engine.py, including:
- ✅ Complete text preprocessing pipeline
- ✅ NLTK sentence splitting with fallback
- ✅ All three chunking strategies  
- ✅ Parameter extraction and flow
- ✅ Sound word replacement system (newly added)

**Next**: Proceed to Phase 3 - Parallel Processing & Candidate Generation

---

## Phase 3: Parallel Processing & Candidate Generation

**FOCUSED SCOPE**: Implement the parallel processing engine

### Task 3.1: Core Parallel Processing Infrastructure ✅ COMPLETED
- [x] **ThreadPoolExecutor Implementation** ✅
  - [x] Ported parallel chunk processing with configurable workers
  - [x] Added progress tracking and monitoring (20%, 40%, 60%, 80%, 100%)
  - [x] Implemented sequential fallback mode when parallel not needed

### Task 3.2: Enhanced Candidate Generation ✅ COMPLETED
- [x] **Multiple Candidates Per Chunk** ✅
  - [x] `num_candidates_per_chunk` logic already implemented
  - [x] `max_attempts_per_candidate` retry logic working
  - [x] Deterministic seed handling (first candidate uses provided seed)
  - [x] Random seed generation for additional candidates working

### Task 3.3: Temporary File Management ✅ COMPLETED
- [x] **Chunk Candidate Storage Strategy** ✅
  - [x] Temporary file naming scheme working
  - [x] Cleanup and resource management in place
  - [x] Memory optimization working for multiple chunks
  - [x] Audio combination from multiple chunks working

**🎯 PHASE 3 STATUS: COMPLETED!**

**Key Achievement**: Parallel processing successfully implemented and tested:
- ✅ **Single chunk**: Automatically uses sequential processing  
- ✅ **Multiple chunks**: Uses ThreadPoolExecutor with progress tracking
- ✅ **Performance**: 5 chunks processed in parallel with 3 workers
- ✅ **Progress Tracking**: Real-time percentage updates (20%, 40%, 60%, 80%, 100%)
- ✅ **Audio Assembly**: Successful combination of parallel-generated chunks

---

## ✅ PHASE 4 STATUS: COMPLETED

**Status**: Phase 4 complete ✅ - Full Whisper validation system and post-processing pipeline implemented  
**Next**: Proceed to Phase 5 - Integration & Final Polish  
**Progress**: 7 of 7 tasks completed  

**Key Achievements Completed:**
- ✅ **Whisper Validation System**: Complete dual backend support with lifecycle management
- ✅ **Full Retry Queue**: Exact Chatter.py retry logic with parallel processing
- ✅ **Enhanced Logging**: Comprehensive progress tracking with timing and status indicators
- ✅ **Comprehensive Testing**: Complete test suite with 6 dedicated Phase 4 test files
- ✅ **Performance Validation**: Core tests pass, backward compatibility maintained
- ✅ **Post-Processing Integration**: Complete auto-editor and ffmpeg normalization support

**Complete TTS Parity Achieved**: The CoreEngine now matches all original Chatter.py TTS functionality

---

### Task 4.1: Whisper Model Management ✅ COMPLETED
- [x] **Dual Backend Support**
  - [x] Implement OpenAI Whisper backend selection
  - [x] Implement faster-whisper backend selection
  - [x] Add model lifecycle management (load → use → cleanup)
  - [x] Add VRAM monitoring and cleanup

### Task 4.2: Validation Pipeline ✅ COMPLETED
- [x] **Port Validation Logic**
  - [x] Implement `whisper_check_mp` function
  - [x] Port fuzzy matching with `difflib.SequenceMatcher`
  - [x] Implement 0.95 threshold validation
  - [x] Add file size and existence checks

### Task 4.3: Retry Mechanism (BASIC) ✅ COMPLETED
- [x] **Failed Chunk Processing**
  - [x] Implement failed chunk identification and queueing
  - [x] Basic fallback candidate selection strategies
  - [ ] **LIMITATION**: Full retry queue with regeneration not implemented

### Task 4.4: Candidate Selection Strategies ✅ COMPLETED
- [x] **Multi-Strategy Selection**
  - [x] Best passed candidate (shortest duration)
  - [x] Fallback strategies (longest transcript vs highest score)
  - [x] Bypass mode (shortest duration without validation)
  - [x] Port exact selection logic from Chatter.py

### Task 4.5: Full Retry Queue Implementation ✅ COMPLETED
- [x] **Analysis & Design Phase**
  - [x] Analyzed current generation flow for retry integration points
  - [x] Designed retry queue structure matching Chatter.py exactly
  - [x] Identified required changes to chunk processing pipeline
  - [x] Implemented complete generation flow with retry support

- [x] **Retry Queue Implementation**
  - [x] Implemented failed chunk identification and retry queue management
  - [x] Added retry loop with configurable max attempts (`max_attempts_per_candidate`)
  - [x] Implemented new seed generation for retry attempts
  - [x] Added parallel retry processing with ThreadPoolExecutor
  - [x] Ensured retry works for both single generation and multi-candidate scenarios

- [x] **Critical Scenarios**
  - [x] **Single Generation Failure**: Retry when `num_candidates_per_chunk=1` and validation fails
  - [x] **All Candidates Fail**: Retry when no candidates pass validation threshold
  - [x] **Partial Chunk Failure**: Retry only for failed chunks while preserving passed ones

### Task 4.6: Enhanced Logging & Comprehensive Testing ✅ COMPLETED
- [x] **Strategic Logging Enhancement**
  - [x] Added INFO level logs for Whisper validation status (enabled/bypassed)
  - [x] Log validation criteria and threshold values (0.95 score, model name, backend)
  - [x] Log candidate selection decisions with scores and reasoning
  - [x] Log retry attempts with attempt numbers and new seeds
  - [x] Added clear indicators for parallel vs sequential processing
  - [x] Enhanced logging with emoji indicators and timing measurements

- [x] **Comprehensive Test Suite**
  - [x] **Created 5 dedicated Phase 4 test files**:
    - [x] `test_phase4_basic_generation.py` - Basic TTS without retry queue
    - [x] `test_phase4_whisper_validation.py` - Whisper validation system
    - [x] `test_phase4_multichunk_generation.py` - Multi-chunk scenarios
    - [x] `test_phase4_enhanced_logging.py` - Enhanced logging validation
    - [x] `test_phase4_comprehensive.py` - Complete Phase 4 test suite
  - [x] **Updated Documentation**: Complete test documentation in `tests/README-chatterpy-migration.md`
  - [x] **Validated Core Tests**: All core tests pass, backward compatibility maintained

### Task 4.7: Post-Processing Integration (Complete TTS Parity) ✅ COMPLETED
- [x] **Auto-Editor Integration**
  - [x] Port `use_auto_editor` logic from Chatter.py (lines 968-989)
  - [x] Implement subprocess call to auto-editor with configurable parameters
  - [x] Handle `keep_original_wav_ae`, `ae_threshold`, `ae_margin` parameters
  - [x] Add proper error handling for auto-editor failures
  - [x] Integrate into post-processing pipeline after speed factor and trimming

- [x] **Audio Normalization Integration**
  - [x] Port `normalize_with_ffmpeg` function from Chatter.py (lines 370-391)
  - [x] Implement EBU and peak normalization methods using ffmpeg-python
  - [x] Handle `normalize_audio`, `normalize_method`, `normalize_level`, `normalize_tp`, `normalize_lra` parameters
  - [x] Add proper error handling for ffmpeg normalization failures
  - [x] Integrate as final post-processing step after auto-editor

- [x] **Post-Processing Pipeline Integration**
  - [x] Add post-processing calls in `_process_tts_generation_sync` after trimming (line 1071)
  - [x] Apply to `final_chunks[0]` (single generation output)
  - [x] Maintain existing file naming and output structure
  - [x] Ensure proper error handling doesn't break the pipeline
  - [x] Update logging to track post-processing steps

- [x] **Parameter Integration & Testing**
  - [x] Verify all post-processing parameters exist in TTSRequest model
  - [x] Create comprehensive test suite `test_phase4_task7_post_processing.py`
  - [x] Test auto-editor integration with various threshold/margin settings
  - [x] Test ffmpeg normalization with EBU and peak methods
  - [x] Validate error handling when auto-editor or ffmpeg not available
  - [x] Ensure backward compatibility when post-processing disabled

---

## Phase 5: Integration & Final Polish

**RENAMED from "Validation & Performance Optimization"**

### Task 5.1: Voice Conversion Enhancement (Quick Win)
- [ ] **Perfect VC Parity**
  - [ ] Refactor `_process_vc_generation_sync` to match Chatter.py chunking exactly
  - [ ] Implement identical crossfading algorithm
  - [ ] Add proper error handling for chunk processing failures

### Task 5.2: Post-Processing Pipeline Integration
- [ ] **Preserve Existing Enhancements**
  - [ ] Ensure speed factor processing works with parallel processing
  - [ ] Ensure trimming works with concatenated audio from multiple chunks
  - [ ] Preserve all existing optimizations

### Task 5.3: Comprehensive Testing & Validation
- [ ] **Feature Parity Validation**
  - [ ] Test all original Chatter.py features produce identical results
  - [ ] Validate parallel vs sequential processing consistency
  - [ ] Test all Whisper models and backend combinations

### Task 5.4: Performance Optimization & Benchmarking
- [ ] **Comparative Performance Testing**
  - [ ] Run identical tasks through Chatter.py and enhanced CoreEngine
  - [ ] Measure total generation time, VRAM usage, CPU utilization
  - [ ] **Goal**: Equal or better performance than original

### Task 5.5: Final Integration & Documentation Updates
- [ ] **Move Updated Endpoints to Main FastAPI Application**
  - [ ] Update `main_api.py` TTS and VC endpoints with changes from `extract_main_api.py`
  - [ ] Uncomment regions of `scripts/test_core_examples.py` that were temporarily commented
  - [ ] Update `docs/api/openapi.yaml` to document new structures and parameters
  - [ ] Run validation script `python scripts/sync_openapi.py`
  - [ ] Run complete validation script `python scripts/test_curl_examples.py --timeout 90`

---

## Success Criteria

1. **Feature Parity**: All original Chatter.py functionality works identically
2. **Performance**: Equal or better processing times than original
3. **Enhanced Features**: All new features (speed, trim, folders, metadata) work seamlessly
4. **Reliability**: Robust error handling and resource management
5. **Scalability**: Handles concurrent requests and large batch processing efficiently

---

## Implementation Notes

- **Incremental Approach**: Each task builds on the previous, allowing for continuous testing
- **Preserve Optimizations**: Maintain all existing performance optimizations
- **Memory First**: Prioritize memory efficiency throughout the implementation
- **Fallback Strategies**: Always provide graceful degradation options
- **Configuration Driven**: Make all new features configurable with sensible defaults
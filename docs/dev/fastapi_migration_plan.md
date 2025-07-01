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

### Task 1.1: Deconstruct Chatter.py TTS Pipeline
- [ ] **Input Handling Flow Analysis**
  - [ ] Map how `generate_batch_tts` differentiates between text input vs single/multiple file uploads
  - [ ] Document the `separate_files_checkbox` logic for generating individual vs combined audio files
  - [ ] Trace the `input_basename` generation and file handling patterns

- [ ] **Text Preprocessing Pipeline Documentation**
  - [ ] Map execution order of preprocessing steps:
    - [ ] `smart_remove_sound_words` (sound word replacement/removal)
    - [ ] `to_lowercase`, `normalize_whitespace`, `fix_dot_letters`, `remove_reference_numbers`
  - [ ] Document the `parse_sound_word_field` and `smart_remove_sound_words` logic

- [ ] **Sentence Processing & Chunking Strategy**
  - [ ] Document `split_into_sentences` using NLTK punkt tokenizer
  - [ ] Map the three chunking strategies:
    - [ ] `enable_batching=True`: `group_sentences(max_chars=400)`
    - [ ] `smart_batch_short_sentences=True`: `smart_append_short_sentences`
    - [ ] Default: Individual sentences
  - [ ] Analyze the chunking decision logic and parameters

- [ ] **Core Generation Loop & Parallel Processing**
  - [ ] Document the `num_generations` outer loop structure
  - [ ] **Critical: Map ThreadPoolExecutor implementation**
    - [ ] Arguments passed to `process_one_chunk`
    - [ ] Parallel vs sequential processing paths (`enable_parallel` flag)
    - [ ] Worker management (`num_parallel_workers_slider`)
    - [ ] Progress tracking and completion handling
  - [ ] Document candidate generation logic per chunk (`num_candidates_per_chunk`, `max_attempts_per_candidate`)

- [ ] **Whisper Validation System Architecture**
  - [ ] **Model Loading Strategy**
    - [ ] OpenAI Whisper vs faster-whisper backend selection
    - [ ] Model size selection and VRAM considerations
    - [ ] Memory management and cleanup patterns
  - [ ] **Validation Pipeline**
    - [ ] `chunk_candidate_map` population and structure
    - [ ] Sequential validation of initial candidates via `whisper_check_mp`
    - [ ] Fuzzy matching logic and scoring (`difflib.SequenceMatcher`)
  - [ ] **Retry Mechanism**
    - [ ] Failed chunk identification and queueing
    - [ ] `while retry_queue` loop logic
    - [ ] Re-generation with new seeds for failed chunks
  - [ ] **Candidate Selection Strategies**
    - [ ] Best score selection for passed validation
    - [ ] Fallback strategies for failed validation:
      - [ ] `use_longest_transcript_on_fail` logic
      - [ ] Highest score fallback
    - [ ] Bypass mode: shortest duration selection

- [ ] **Audio Assembly & Post-Processing**
  - [ ] Document `torch.cat` concatenation of selected chunks
  - [ ] Map existing post-processing in Chatter.py:
    - [ ] Auto-editor integration (`use_auto_editor`, threshold, margin)
    - [ ] FFmpeg normalization (`normalize_audio`, EBU/peak methods)
  - [ ] Document format conversion and export logic

### Task 1.2: Analyze Chatter.py Voice Conversion
- [ ] **Chunking Logic**
  - [ ] Document `chunk_sec` threshold decision (≤60s = direct processing)
  - [ ] Map chunking parameters (`chunk_sec`, `overlap_sec`)
  - [ ] Analyze chunk processing loop and temporary file handling

- [ ] **Cross-fade Implementation**
  - [ ] Document the crossfading algorithm for chunk stitching
  - [ ] Map fade-in/fade-out calculations (`np.linspace`)
  - [ ] Analyze overlap handling and concatenation logic

### Task 1.3: Current core_engine_fixed.py Analysis
- [ ] **Document Current TTS Flow**
  - [ ] Map `generate_tts` → `_process_tts_generation_sync` → `_combine_audio_chunks`
  - [ ] Identify current simplifications vs original (first candidate selection, no Whisper)
  - [ ] Document current chunk processing approach

- [ ] **Document Current VC Flow**
  - [ ] Map `generate_vc` → `_process_vc_generation_sync`
  - [ ] Compare chunking implementation with Chatter.py

- [ ] **Document New Features Implementation**
  - [ ] Speed factor processing optimization (`apply_speed_factor_post_processing`)
  - [ ] Audio trimming pipeline (`_apply_trimming_post_processing`)
  - [ ] Project folder organization
  - [ ] Metadata generation and CSV/JSON export
  - [ ] Enhanced filename generation

### Task 1.4: Create Comprehensive Feature Gap Report
Create a detailed comparison matrix:

| Feature Category | Chatter.py Implementation | core_engine_fixed.py Status | Priority | Notes |
|------------------|---------------------------|------------------------------|----------|-------|
| **Parallel Processing** | ThreadPoolExecutor with configurable workers | Missing | Critical | Core performance feature |
| **Whisper Validation** | Full pipeline with retries | Missing | Critical | Quality assurance |
| **Candidate Selection** | Sophisticated scoring + fallbacks | Simplified (first only) | Critical | Affects output quality |
| **Text Preprocessing** | Complete pipeline | Partial | High | Affects input handling |
| **Chunking Strategies** | 3 modes with smart batching | Basic | High | Affects processing efficiency |
| **Batch File Processing** | Multiple files + separate outputs | Missing | High | User workflow feature |
| **Sound Word Replacement** | Full find/replace system | Missing | Medium | Text customization |
| **Speed Factor** | Not available | **Enhanced** | - | New feature to preserve |
| **Audio Trimming** | Not available | **Enhanced** | - | New feature to preserve |
| **Project Folders** | Not available | **Enhanced** | - | New feature to preserve |
| **Metadata Generation** | Basic settings export | **Enhanced** | - | New feature to preserve |

---

## Phase 2: Architectural Design & Integration Strategy

Design the target architecture that seamlessly integrates original features with new enhancements.

### Task 2.1: Design Enhanced CoreEngine Architecture
- [ ] **Method Decomposition Strategy**
  - [ ] Design modular private methods structure:
    ```
    generate_tts()
    ├── _prepare_text_and_params()
    ├── _process_input_files() [NEW - for batch processing]
    ├── _create_sentence_groups()
    ├── _generate_chunk_candidates_parallel()
    ├── _validate_with_whisper() [NEW]
    ├── _select_best_candidates() [NEW]
    ├── _assemble_base_audio()
    ├── _apply_post_processing_pipeline() [EXISTING - speed, trim]
    └── _finalize_outputs() [EXISTING - formats, metadata]
    ```

- [ ] **Memory Management Design**
  - [ ] Whisper model lifecycle management (load → use → cleanup)
  - [ ] Temporary file management for parallel processing
  - [ ] CUDA memory optimization strategies

- [ ] **Error Handling & Resilience**
  - [ ] Integration with existing error tracking system `docs/api/monitoring/README.md`
  - [ ] Graceful degradation strategies (parallel → sequential, Whisper → bypass)
  - [ ] Resource cleanup on failures
  - [ ] Review and update `docs/api/guides/error-handling.md`

### Task 2.2: Post-Processing Pipeline Integration
- [ ] **Define Clear Data Flow**
  ```
  Input Processing → Text Preprocessing → Sentence Grouping 
  → Parallel Generation → Whisper Validation → Candidate Selection 
  → Audio Assembly → **Post-Processing Pipeline** → Output Finalization
  ```

- [ ] **Post-Processing Sequence Design**
  - [ ] Speed factor application (preserve existing optimization)
  - [ ] Audio trimming (preserve existing implementation)
  - [ ] Format conversion
  - [ ] Metadata generation
  - [ ] Project folder organization
  - [ ] Review and update `docs/api/guides/advanced-features.md`

### Task 2.3: API Contract Enhancement
- [ ] **Extend TTSRequest Model**
  Add parameters for full feature parity:
  ```python
  # Parallel Processing
  enable_parallel: bool = True
  num_parallel_workers: int = 4
  
  # Whisper Validation
  bypass_whisper_checking: bool = False
  whisper_model_name: str = "medium"
  use_faster_whisper: bool = True
  use_longest_transcript_on_fail: bool = True
  
  # Candidate Generation
  num_candidates_per_chunk: int = 3
  max_attempts_per_candidate: int = 3
  
  # Text Processing
  sound_words_field: str = ""
  
  # Batch Processing
  process_files_separately: bool = False
  ```

- [ ] **API Response Enhancements**
  - [ ] Add generation statistics (chunks processed, retries, etc.) Look at `docs/api/monitoring/README.md`
  - [ ] Include processing time breakdown
  - [ ] Add alternative format URLs for streaming responses
  - [ ] Update or create the documentation at `docs/api/monitoring/`

---

## Phase 3: Implementation - Core Logic Migration

Systematic implementation of enhanced features while preserving existing capabilities.

### Task 3.1: Voice Conversion Enhancement (Quick Win)
- [ ] **Perfect VC Parity**
  - [ ] Refactor `_process_vc_generation_sync` to exactly match Chatter.py chunking
  - [ ] Implement identical crossfading algorithm
  - [ ] Add proper error handling for chunk processing failures
  - [ ] Validate memory efficiency with existing implementation

### Task 3.2: API Plumbing & Parameter Flow
- [ ] **Update API Layer**
  - [ ] Modify `extract_main_api.py` to accept new parameters
  - [ ] Update form data handling for file uploads + parameters
  - [ ] Ensure parameter validation and defaults

- [ ] **Engine Parameter Integration**
  - [ ] Modify `CoreEngine.generate_tts` signature
  - [ ] Add parameter validation and sanitization
  - [ ] Implement parameter inheritance and defaults

### Task 3.3: Text Processing & Preparation Pipeline
- [ ] **Port Complete Preprocessing**
  - [ ] Implement `smart_remove_sound_words` with pattern matching
  - [ ] Port all text normalization functions
  - [ ] Add preprocessing parameter controls

- [ ] **Sentence Processing Enhancement**
  - [ ] Implement NLTK-based sentence splitting with fallbacks
  - [ ] Port all three chunking strategies with exact logic
  - [ ] Add chunking parameter validation

- [ ] **Batch File Processing**
  - [ ] Implement multiple file handling
  - [ ] Add separate vs combined output logic
  - [ ] Integrate with existing project folder structure

### Task 3.4: Parallel Generation System
- [ ] **Candidate Generation Engine**
  - [ ] Port `process_one_chunk` logic with exact TTS parameters
  - [ ] Implement ThreadPoolExecutor-based parallel processing
  - [ ] Add sequential processing fallback
  - [ ] Implement progress tracking and monitoring

- [ ] **Memory-Efficient Processing**
  - [ ] Design chunk candidate storage strategy
  - [ ] Implement temporary file management
  - [ ] Add VRAM monitoring and warnings

### Task 3.5: Whisper Validation System (Most Complex)
- [ ] **Model Management**
  - [ ] Implement dual backend support (OpenAI + faster-whisper)
  - [ ] Add model size selection and VRAM validation
  - [ ] Design model lifecycle (load → use → cleanup pattern)

- [ ] **Validation Pipeline**
  - [ ] Port `whisper_check_mp` with exact matching logic
  - [ ] Implement batch validation of candidates
  - [ ] Add validation scoring and threshold checking

- [ ] **Retry Mechanism**
  - [ ] Implement failed chunk identification
  - [ ] Port retry queue processing logic
  - [ ] Add configurable retry limits and strategies

- [ ] **Candidate Selection Intelligence**
  - [ ] Implement multi-strategy selection (score, length, duration)
  - [ ] Add fallback logic for validation failures
  - [ ] Port bypass mode with shortest duration selection

### Task 3.6: Audio Assembly & Post-Processing Integration
- [ ] **Enhanced Audio Assembly**
  - [ ] Implement torch.cat-based concatenation
  - [ ] Add audio format validation and normalization
  - [ ] Ensure compatibility with existing post-processing

- [ ] **Post-Processing Pipeline Enhancement**
  - [ ] Integrate speed factor processing with new assembly logic
  - [ ] Ensure trimming works with concatenated audio
  - [ ] Preserve all existing optimizations

### Task 3.7: Resource Management & Cleanup
- [ ] **Memory Management**
  - [ ] Implement proper Whisper model cleanup
  - [ ] Add CUDA cache management
  - [ ] Design temporary file lifecycle management

- [ ] **Error Recovery**
  - [ ] Add graceful degradation (parallel → sequential)
  - [ ] Implement resource cleanup on failures
  - [ ] Add comprehensive error logging

---

## Phase 4: Validation & Performance Optimization

Ensure correctness, performance, and reliability of the enhanced system.

### Task 4.1: Comprehensive Functional Testing
- [ ] **Feature Parity Validation**
  - [ ] Test all original Chatter.py features produce identical results
  - [ ] Validate parallel vs sequential processing consistency
  - [ ] Test all Whisper models and backend combinations
  - [ ] Verify all chunking strategies produce expected outputs

- [ ] **New Features Integration Testing**
  - [ ] Test speed factor with parallel processing and Whisper validation
  - [ ] Test trimming with batch processing and multiple generations
  - [ ] Test metadata generation with all parameter combinations
  - [ ] Test project folder organization with batch processing

- [ ] **Edge Case & Error Handling Testing**
  - [ ] Test with very long texts (>10k characters)
  - [ ] Test with various audio formats and sample rates
  - [ ] Test memory pressure scenarios
  - [ ] Test network interruption during downloads

### Task 4.2: Performance Benchmarking & Optimization
- [ ] **Comparative Performance Testing**
  - [ ] Run identical tasks through Chatter.py and enhanced CoreEngine
  - [ ] Measure total generation time, VRAM usage, CPU utilization
  - [ ] Test with various parallel worker configurations
  - [ ] **Goal**: Equal or better performance than original

- [ ] **Scalability Testing**
  - [ ] Test concurrent API requests
  - [ ] Test large batch processing (10+ files)
  - [ ] Test memory usage under sustained load
  - [ ] Optimize resource allocation and cleanup

- [ ] **Memory Profiling & Optimization**
  - [ ] Profile VRAM usage throughout generation pipeline
  - [ ] Optimize temporary file storage
  - [ ] Ensure no memory leaks in long-running processes

### Task 4.3: Final Integration & Polish
- [ ] **Move the updated end points to the main FastAPI application**
  - [ ] Update `main_api.py` TTS and VC end points with our changes in `extract_main_api.py`
  - [ ] Uncomment the regions of `scripts/test_core_examples.py` that were temporarily commented, and ensure they succeed
  - [ ] Update `docs/api/openapi.yaml` as to document the new structures and parameters added/changed in the first step of this task
  - [ ] Run the validation script `python scripts/sync_openapi.py`
  - [ ] Run the complete validation script `python scripts/test_curl_examples.py --timeout 90` that tests most of the full API method set

- [ ] **Code Quality & Documentation**
  - [ ] Add comprehensive docstrings for all new methods
  - [ ] Implement consistent error messages and logging
  - [ ] Add configuration validation and helpful error messages

- [ ] **API Documentation & Examples**
  - [ ] Update API documentation with new parameters
  - [ ] Create example requests for common use cases
  - [ ] Document performance recommendations

- [ ] **Monitoring & Observability**
  - [ ] Add detailed metrics for parallel processing performance
  - [ ] Implement Whisper validation statistics
  - [ ] Add processing time breakdown in responses

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
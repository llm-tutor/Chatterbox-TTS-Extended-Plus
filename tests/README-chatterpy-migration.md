# Chatter.py Migration Tests

This directory contains tests specifically for validating the migration of features from the original `Chatter.py` (Gradio-based) implementation to the enhanced `core_engine.py` (FastAPI-based) implementation.

## Migration Project Overview

**Goal**: Migrate sophisticated TTS/VC generation logic from `Chatter.py` into the structured `CoreEngine` class while preserving and enhancing all existing features.

**Migration Phases**:
- ✅ **Phase 1**: Deep Analysis & Feature Mapping (Completed)
- ✅ **Phase 2**: Foundation Enhancement & Text Processing (Completed) 
- ✅ **Phase 3**: Parallel Processing & Candidate Generation (Completed)
- ✅ **Phase 4**: Whisper Validation System (Completed)
- ✅ **Phase 5**: Integration & Final Polish (Completed)

## Test Files

### Phase 2 & 3 Tests ✅

#### `test_parallel_processing_phases2_3.py`
**Purpose**: Validate parallel processing implementation with ThreadPoolExecutor

**Tests**:
- **Sequential Processing**: Single sentence → automatic sequential processing
- **Parallel Processing**: Multiple sentences → ThreadPoolExecutor with progress tracking  
- **Parallel Disabled**: Force sequential even with multiple sentences

**Key Validations**:
- Automatic parallel vs sequential selection logic
- Progress tracking during parallel generation (20%, 40%, 60%, 80%, 100%)
- Multi-chunk audio assembly 
- Parameter flow for `enable_parallel` and `num_parallel_workers`

**Expected Log Evidence**:
```
"Split text into 5 sentences"
"Processing 5 chunks in parallel with 3 workers"  
"[PROGRESS] Generated chunk 1/5 (20%)"
"Combined 5 chunks to: outputs\..."
```

**Usage**:
```bash
# Ensure server is running
python tests/test_parallel_processing_phases2_3.py
```

### Phase 4 Tests ✅

#### `test_phase4_basic_generation.py`
**Purpose**: Validate basic TTS generation with bypass_whisper_checking=True

**Tests**:
- **Basic Generation**: Single chunk, bypass validation
- **Backward Compatibility**: Ensure retry queue doesn't break existing functionality
- **Performance**: ~8-15 seconds expected

**Key Validations**:
- Status 200 response
- Sequential processing for single chunk
- Bypassed Whisper validation
- Normal output generation

**Expected Log Evidence**:
```
"Bypassing Whisper validation - selecting shortest duration candidates"
"Processing 1 chunks sequentially"
"Single chunk copied to: outputs\..."
```

#### `test_phase4_whisper_validation.py`
**Purpose**: Validate Whisper validation system with enhanced logging

**Tests**:
- **Whisper Loading**: Model initialization and backend selection
- **Validation Pipeline**: Complete fuzzy matching and scoring
- **Enhanced Logging**: Comprehensive progress tracking
- **Performance**: ~25-40 seconds including model loading

**Key Validations**:
- Whisper model loading (faster-whisper backend)
- Validation criteria logging (score >= 0.95 threshold)
- Timing measurements and progress indicators
- Candidate selection with detailed feedback

**Expected Log Evidence**:
```
"Running Whisper validation on X candidates"
"Validation criteria: score >= 0.95 threshold, model: WhisperModel"
"Initial validation completed in X.Xs"
"✅ All chunks passed initial validation - no retry needed"
"[Chunk 0] ✅ Selected validated candidate: ... (PASSED Whisper)"
```

#### `test_phase4_multichunk_generation.py`
**Purpose**: Test multi-chunk generation with higher chance of retry scenarios

**Tests**:
- **Multi-Chunk Processing**: 5 sentences with batching
- **Multiple Candidates**: 3 candidates per chunk
- **Complex Validation**: Higher chance of triggering retry logic
- **Performance**: ~40-60 seconds for complex scenarios

**Key Validations**:
- Sentence splitting and batching behavior
- Multiple candidate generation and validation
- Potential retry queue activation
- Multi-chunk audio assembly

**Expected Log Evidence**:
```
"Split text into 5 sentences"
"Created X sentence groups" (batching effect)
"Running Whisper validation on X candidates"
"Processing evidence (sequential or parallel)"
```

#### `test_phase4_enhanced_logging.py`
**Purpose**: Validate enhanced logging system from Task 4.6

**Tests**:
- **Logging Quality**: Emoji indicators and clear formatting
- **Timing Measurements**: Performance analysis capabilities
- **Progress Visibility**: Comprehensive process transparency
- **Debug Information**: Detailed validation feedback

**Key Validations**:
- Enhanced logging features with emojis (✅❌🔄⚠️🎯🏁)
- Validation criteria and retry configuration logging
- Timing measurements for performance analysis
- Detailed candidate selection process

**Expected Log Evidence**:
```
"🎯 Final candidate selection:"
"🏁 Complete validation finished in X.Xs (including 0 retry attempts)"
"[Chunk 0] ✅ Selected validated candidate: ... (duration=X.XXs, PASSED Whisper)"
"🏁 Final selection: X chunks ready for assembly"
```

#### `test_phase4_comprehensive.py`
**Purpose**: Run complete Phase 4 test suite in sequence

**Tests**:
- **All Phase 4 Tests**: Sequential execution of all Phase 4 tests
- **Core Tests Integration**: Backward compatibility validation
- **Complete Validation**: End-to-end Phase 4 verification
- **Performance Summary**: Overall timing and success metrics

**Key Validations**:
- All individual tests pass
- Core tests still pass (backward compatibility)
- Performance within acceptable ranges
- Complete feature set working

**Usage**:
```bash
# Run complete Phase 4 validation
python tests/test_phase4_comprehensive.py
```

#### `test_phase4_task7_post_processing.py`
**Purpose**: Validate Task 4.7 post-processing integration (auto-editor and ffmpeg normalization)

**Tests**:
- **Basic TTS Baseline**: Generation without post-processing for comparison
- **Auto-Editor Integration**: Complete auto-editor post-processing with all parameters
- **FFmpeg EBU Normalization**: EBU R128 loudness normalization testing
- **FFmpeg Peak Normalization**: Peak normalization with dynaudnorm filter
- **Complete Pipeline**: Both auto-editor and ffmpeg normalization together
- **Integration Testing**: Post-processing with existing features (speed factor, trimming)

**Key Validations**:
- Post-processing parameters correctly applied
- Auto-editor --no-open flag prevents file opening
- FFmpeg cross-drive compatibility with shutil.move()
- Complete post-processing pipeline order (Speed → Trimming → Auto-Editor → FFmpeg)
- Error handling when tools are not available

**Expected Log Evidence**:
```
"🎨 Applying post-processing pipeline..."
"🎬 Applying auto-editor post-processing to: ..."
"   🔧 Running command: auto-editor --edit audio:threshold=0.06 --margin 0.2s --export audio --no-open ..."
"   ✅ Auto-editor post-processing completed: ..."
"🔊 Applying ffmpeg normalization to: ..."
"   🔧 EBU normalization filter: loudnorm=I=-24.0:TP=-2.0:LRA=7.0"
"   ✅ FFmpeg normalization completed: ..."
```

**Usage**:
```bash
# Test post-processing integration
python tests/test_phase4_task7_post_processing.py
```

### Phase 5 Tests ✅

#### `test_phase5_task1_vc_enhancement.py`
**Purpose**: Validate Task 5.1 Voice Conversion enhancements with improved error handling and logging

**Tests**:
- **Short Audio VC**: Direct processing for audio ≤60s without chunking
- **Long Audio Chunking**: Chunking with crossfading for audio >60s
- **Error Handling**: Proper error propagation instead of silence fallback

**Key Validations**:
- Enhanced error handling (no silence fallback)
- Improved logging with emoji indicators and timing
- Crossfading algorithm matching Chatter.py exactly
- Proper cleanup of temporary files with finally blocks
- Chunk count estimation and processing feedback

**Expected Log Evidence**:
```
"🎯 Processing short audio directly (4.52s ≤ 60s)"
"🔄 Processing long audio with chunking: 60s chunks, 0.1s overlap (90.0s total)"
"📊 Expected 2 chunks (1323000 samples each, 2205 overlap)"
"✅ Chunk 0.0s-60.0s processed successfully"
"🎵 Combining 2 chunks with crossfading (overlap: 2205 samples)..."
"✅ Combined VC result saved: outputs\... (89.95s)"
```

#### `test_phase5_task2_post_processing_integration.py`
**Purpose**: Validate Task 5.2 post-processing pipeline integration with parallel processing

**Tests**:
- **Speed Factor with Parallel**: Speed factor processing works with parallel-generated chunks
- **Trimming with Concatenation**: Audio trimming works with concatenated audio from multiple chunks
- **Post-Processing Integration**: Auto-editor and normalization integrate properly
- **Optimization Preservation**: Zero overhead for speed_factor=1.0 maintained

**Key Validations**:
- Speed factor applied correctly after chunk combination
- Trimming works on final concatenated audio
- Post-processing pipeline executes in correct order
- Existing optimizations preserved

**Expected Log Evidence**:
```
"Phase 10.1.2 Optimization: Separate speed factor processing"
"Step 1: Combine chunks (always at 1.0x speed)"
"Step 2: Apply speed factor as post-processing if needed"
"Step 3: Apply trimming as post-processing if requested"
"🎨 Applying post-processing pipeline..."
```

#### `test_phase5_task3_comprehensive_validation.py`
**Purpose**: Validate Task 5.3 comprehensive testing and feature parity with original Chatter.py

**Tests**:
- **Original Features Parity**: All original Chatter.py features work identically
- **Parallel vs Sequential Consistency**: Both processing modes produce consistent results
- **Whisper Models and Backends**: Test different Whisper configurations

**Key Validations**:
- Complete parameter compatibility with original Chatter.py
- Consistent results between parallel and sequential processing
- All Whisper backends (faster-whisper + OpenAI) working
- Comprehensive feature integration

**Expected Log Evidence**:
```
"Text preprocessing (original features)"
"Chunking strategies (original features)"
"Parallel processing (original features)"
"Whisper validation (original features)"
"✅ Both processing modes completed"
"✅ Both Whisper backends completed"
```

#### `test_phase5_task4_performance_benchmarking.py`
**Purpose**: Validate Task 5.4 performance optimization and benchmarking

**Tests**:
- **Single Chunk Performance**: Baseline performance measurement
- **Parallel Processing Performance**: Multi-chunk performance with resource monitoring
- **Whisper Validation Performance**: Performance with validation enabled
- **Resource Usage Efficiency**: Memory usage and cleanup validation

**Key Validations**:
- Performance monitoring with CPU and memory tracking
- Processing times within expected ranges
- Resource efficiency and cleanup
- Performance meets or exceeds original Chatter.py

**Expected Log Evidence**:
```
"⚡ Testing Single Chunk Performance..."
"📊 Memory: 850.1MB"
"📊 CPU: 45.2%"
"🚀 Testing Parallel Processing Performance..."
"🎤 Testing Whisper Validation Performance..."
"📊 Testing Resource Usage Efficiency..."
```

**Performance Targets**:
- Single chunk: < 120 seconds
- Parallel processing: < 300 seconds
- Whisper validation: < 400 seconds
- Memory increase: < 500MB for small tests

## Features Successfully Migrated ✅

### Text Processing Pipeline
- **Sound Word Replacement**: Smart find/replace with possessive/quote handling
- **5-Step Preprocessing**: Lowercase, whitespace, dot letters, reference numbers
- **NLTK Integration**: Sentence splitting with fallback
- **Enhanced Chunking**: Three strategies (batching, smart batching, individual)

### Parallel Processing Infrastructure  
- **ThreadPoolExecutor**: Configurable parallel workers (1-16)
- **Smart Logic**: Automatic parallel vs sequential based on chunk count
- **Progress Tracking**: Real-time percentage updates
- **Candidate Generation**: Multiple candidates per chunk with retry logic
- **Audio Assembly**: Combination of parallel-generated chunks

### Whisper Validation System ✅
- **Dual Backend Support**: OpenAI Whisper and faster-whisper
- **Model Management**: Lifecycle management with VRAM cleanup
- **Validation Pipeline**: Complete fuzzy matching with difflib.SequenceMatcher
- **Quality Scoring**: 0.95 threshold validation with fallback strategies
- **Full Retry Queue**: Failed chunk regeneration with new seeds
- **Enhanced Logging**: Comprehensive progress tracking with emoji indicators

### API Enhancements
- **New Parameters**: `enable_parallel`, `num_parallel_workers`, `bypass_whisper_checking`
- **Whisper Configuration**: `whisper_model`, `use_faster_whisper`, `use_longest_transcript_on_fail`
- **Configuration**: Defaults in config.yaml
- **Backward Compatibility**: All existing functionality preserved

## Next Phase Tests (Future)

### Phase 4: Whisper Validation System
- **Dual Backend Tests**: OpenAI Whisper vs faster-whisper
- **Validation Pipeline**: Fuzzy matching and quality scoring
- **Retry Mechanism**: Failed chunk re-generation
- **Candidate Selection**: Multi-strategy selection logic

### Phase 5: Integration & Polish
- **Performance Comparison**: Chatter.py vs enhanced core_engine.py
- **Memory Profiling**: VRAM usage optimization
- **Comprehensive Feature Parity**: All original features working

## Running Migration Tests

### Prerequisites
```bash
# Ensure server is running
python main.py  # or uvicorn main:app --host 127.0.0.1 --port 7860

# Verify server health
curl http://127.0.0.1:7860/api/v1/health
```

### Test Execution
```bash
# Phase 2 & 3 validation
python tests/test_parallel_processing_phases2_3.py

# Core validation (includes migration features)
python scripts/test_core_examples.py
```

### Server Log Monitoring
```bash
# Monitor real-time processing (Windows)
Get-Content logs\chatterbox_extended.log -Wait -Tail 20

# Check for parallel processing evidence
# Look for: "Processing X chunks in parallel with Y workers"
# Look for: "[PROGRESS] Generated chunk X/Y (Z%)"
```

## Migration Success Criteria

### Phase 2 & 3 ✅ COMPLETED
- [x] All text preprocessing functions working
- [x] NLTK sentence splitting with fallback  
- [x] All chunking strategies implemented
- [x] Parallel processing with ThreadPoolExecutor
- [x] Progress tracking and monitoring
- [x] Audio assembly from multiple chunks
- [x] Backward compatibility maintained

### Phase 4 ✅ COMPLETED
- [x] Whisper model management (dual backend)
- [x] Validation pipeline with fuzzy matching
- [x] Full retry queue for failed chunks
- [x] Candidate selection strategies
- [x] Enhanced logging with timing and emojis
- [x] Performance optimization and monitoring
- [x] Complete Chatter.py retry logic implementation

### Phase 5 ✅ COMPLETED
- [x] Voice Conversion enhancement with improved error handling
- [x] Post-processing pipeline integration with parallel processing
- [x] Comprehensive feature parity validation
- [x] Performance optimization and benchmarking
- [x] Final integration and production readiness

### Complete Migration Success ✅
- [x] All original Chatter.py features migrated successfully
- [x] Enhanced with modern FastAPI architecture
- [x] Parallel processing with ThreadPoolExecutor
- [x] Dual-backend Whisper validation system
- [x] Complete post-processing pipeline
- [x] Performance parity or better achieved
- [x] Production-ready with comprehensive testing

## Documentation

- **Implementation Plan**: `docs/dev/fastapi_migration_plan.md`
- **Phase 1 Analysis**: `docs/dev/phase1_analysis_report.md`  
- **Changelog**: `docs/changelog.md`
- **Foundation Protocols**: `docs/dev/implementation-protocols.md`

---

**Status**: Phase 5 complete - FastAPI Migration Project 100% COMPLETED ✅
**Achievement**: Full feature parity with original Chatter.py + enhanced capabilities

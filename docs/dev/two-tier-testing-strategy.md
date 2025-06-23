# Two-Tier cURL Testing Strategy - Implementation Plan

## Overview
Implement a balanced approach to cURL example testing that serves both implementation workflow efficiency and comprehensive developer documentation needs.

## Problem Statement
Current comprehensive cURL testing requires 8-15 minutes (5 TTS + 3 VC generations), which is impractical for routine implementation phase validation but necessary for complete documentation coverage.

## Solution: Two-Tier Testing Strategy

### Tier 1: Core Validation (Implementation Protocol)
**Purpose**: Quick validation during implementation phase closing  
**Time Target**: 2-3 minutes maximum  
**Coverage**: Universal examples that work on any setup  

**Examples Included**:
- Health check (instant)
- Basic TTS without reference voice (15-60 seconds)
- Basic VC with existing project files (15-60 seconds)
- List voices endpoint (instant)
- List outputs endpoint (instant)
- 1-2 error demonstrations (instant)

**Total**: 1 TTS + 1 VC + 4 non-generative = ~2-3 minutes

### Tier 2: Comprehensive Documentation (Developer Reference)  
**Purpose**: Complete example validation for developers  
**Time Target**: 8-15 minutes (acceptable for thorough validation)  
**Coverage**: All documented examples including advanced features  
**Usage**: Documentation releases, major API changes, developer onboarding  

**Examples Included**: All current examples (5 TTS + 3 VC + others)

## Implementation Tasks

> **📁 Current Scripts Documentation**: See [`scripts/README.md`](../../scripts/README.md) for existing validation scripts

### Task 1: Create Core Examples Test Script
**File**: `scripts/test_core_examples.py`
**Timeout**: 60 seconds per request
**Documentation**: Update `scripts/README.md` with new script details
**Content**:
```python
core_tests = [
    # Instant responses
    ("Health Check", "GET", "/api/v1/health"),
    ("List Voices", "GET", "/api/v1/voices"), 
    ("List Outputs", "GET", "/api/v1/outputs"),
    
    # Generation tests (no reference voice requirements)
    ("Basic TTS", "POST", "/api/v1/tts", {
        "text": "Hello, this is a core validation test.",
        "export_formats": ["wav"]
    }),
    ("Basic VC", "POST", "/api/v1/vc", {
        "input_audio_source": "hello_quick_brown.wav",  # existing project file
        "target_voice_source": "speaker_en/DAVID-2.mp3",  # existing project file
        "export_formats": ["wav"]
    }),
    
    # Error demonstration
    ("Error Demo", "POST", "/api/v1/tts", {
        "temperature": 2.0  # Invalid parameter
    })
]
```

### Task 2: Update Comprehensive Test Script
**File**: `scripts/test_curl_examples.py`
**Changes**:
- Increase timeout to 90 seconds per request
- Add total time estimation output
- Add progress indicators for long-running tests

### Task 3: Reorganize cURL Examples Documentation
**File**: `docs/api/schemas/examples/curl-examples.md`

**New Structure**:
```markdown
# cURL Examples

## Core Examples (Implementation Validation)
> **Purpose**: Quick validation tests that work on any setup
> **Time**: 2-3 minutes
> **Requirements**: No specific voice files needed

### Basic TTS (No Reference Voice)
### Basic VC (Using Project Files)
### Health & Status Endpoints
### Error Handling Examples

## Advanced Examples (Developer Reference)  
> **Purpose**: Complete feature demonstration
> **Time**: 8-15 minutes  
> **Requirements**: Specific voice files must exist (see setup notes)

### Voice Cloning Examples
### Advanced Parameter Examples  
### File Upload Examples
### Complex Scenarios
```

### Task 4: Add Setup Documentation
**Files**: 
- `docs/api/schemas/examples/curl-examples.md`
- `docs/api/quick-start.md`

**Content**:
```markdown
## Voice File Requirements for Advanced Examples

Advanced cURL examples require specific reference voice files to be present:

**Required Files**:
- `reference_audio/speaker_en/DAVID-2.mp3` 
- `reference_audio/speaker_en/CONNOR-2-non-native.mp3`
- `vc_inputs/hello_quick_brown.wav`
- `vc_inputs/alex.mp3`

**Setup Instructions**:
1. Ensure these files exist in your project setup
2. Use `curl http://localhost:7860/api/v1/voices` to verify available voices
3. Replace file references in examples with your available voices if needed

**For Core Examples**: No specific voice files required - they work universally
```

### Task 5: Update Implementation Protocol Documentation
**File**: `docs/api/how-to-update-api-docs.md`
**Additional**: Update `scripts/README.md` with new scripts

**Add Section**:
```markdown
## Testing Protocol for Implementation Phases

### Quick Validation (2-3 minutes)
```bash
python scripts/test_core_examples.py
```
Use this for routine implementation phase closing validation.

### Comprehensive Validation (8-15 minutes)  
```bash
python scripts/test_curl_examples.py --timeout 90
```
Use this for major releases, documentation updates, or thorough validation.

### Smoke Test (30 seconds)
```bash  
python scripts/test_working_examples.py
```
Use this for quick health checks during development.
```

### Task 6: Update Project Automation Scripts
**Files**: Any CI/CD or automation scripts

**Changes**:
- Use core validation for regular builds
- Use comprehensive validation for releases
- Document timeout requirements

## Success Criteria

### Implementation Workflow
- [ ] Core validation completes in 2-3 minutes consistently
- [ ] Core examples work universally without specific voice file requirements
- [ ] Quick feedback loop supports efficient development

### Documentation Quality  
- [ ] Comprehensive validation covers all documented examples
- [ ] Advanced examples work correctly with proper setup
- [ ] Clear separation between core and advanced use cases
- [ ] Setup requirements clearly documented

### Developer Experience
- [ ] New developers can run core examples immediately
- [ ] Advanced examples work when setup requirements are met
- [ ] Clear guidance on which test to use when
- [ ] Reasonable time investment for each validation level

## Integration with API Reorganization Project

This task extends **Phase 4.6: Final Refinements** of the API documentation reorganization project.

**Status**: Ready for implementation after current reorganization completion
**Dependencies**: Completion of current cURL testing script fixes
**Timeline**: 1-2 sessions to implement all components

## Notes

- Core examples should remain stable and universal
- Advanced examples can evolve with API capabilities  
- Testing strategy should be documented for future maintainers
- Consider adding this approach to other example formats (Python, etc.)

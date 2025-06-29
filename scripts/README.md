# Validation Scripts

This directory contains automated validation and testing scripts for the API documentation project.

## Script Overview

| Script | Purpose | Usage | Time |
|--------|---------|-------|------|
| **test_core_examples.py** | Core validation suite (implementation protocol) | `python scripts/test_core_examples.py` | ~2-3 minutes |
| **test_working_examples.py** | Alternative core working examples validation | `python scripts/test_working_examples.py` | ~2-3 minutes |
| **test_curl_examples.py** | Comprehensive cURL testing (all examples) | `python scripts/test_curl_examples.py --timeout 90` | ~8-15 minutes |
| **test_integrated_tts_file_management.py** | Complete TTS file management workflow | `python scripts/test_integrated_tts_file_management.py` | ~3-5 minutes |
| **test_integrated_vc_input_management.py** | Complete VC input file management workflow | `python scripts/test_integrated_vc_input_management.py` | ~3-5 minutes |
| **test_integrated_voice_management.py** | Complete voice management workflow | `python scripts/test_integrated_voice_management.py` | ~3-5 minutes |
| **check_links.py** | Validates internal documentation links | `python scripts/check_links.py` | ~30 seconds |
| **sync_openapi.py** | Checks OpenAPI spec sync with live API | `python scripts/sync_openapi.py` | ~10 seconds |
| **test_examples.py** | Tests Python code examples in docs | `python scripts/test_examples.py` | ~60 seconds |
| **diagnose_curl_examples.py** | Analyzes cURL examples without requests | `python scripts/diagnose_curl_examples.py` | ~5 seconds |
| **test_phase11_tts_reference_file_times_test.py** | Tests times with different voice references | `python scripts/test_phase11_tts_reference_file_times_test.py` | ~20 minutes |

## Usage by Scenario

> **Two-Tier Testing Strategy**: Use appropriate validation tier based on development stage and requirements

### Tier 1: Core Validation (Implementation Protocol)
**Target Time**: 2-3 minutes | **Usage**: Routine development validation, implementation phase closing

```bash
# Primary: Core validation suite (implementation protocol)
python scripts/test_core_examples.py

# Alternative: Working examples validation  
python scripts/test_working_examples.py

# API sync verification
python scripts/sync_openapi.py
```

### Tier 2: Comprehensive Validation (Release Quality)  
**Target Time**: 8-15 minutes | **Usage**: Major releases, documentation updates, developer onboarding

```bash
# Full cURL examples validation
python scripts/test_curl_examples.py --timeout 90

# Complete validation suite
python scripts/check_links.py
python scripts/sync_openapi.py  
python scripts/test_examples.py
```

### Tier 3: Integrated Workflow Testing (Phase 11+)
**Target Time**: 3-5 minutes per test | **Usage**: Complete workflow validation, feature demonstration

```bash
# TTS file management workflow (generation, organization, cleanup)
python scripts/test_integrated_tts_file_management.py

# VC input management workflow (upload, organization, cleanup)  
python scripts/test_integrated_vc_input_management.py

# Voice management workflow (upload, metadata, organization, cleanup)
python scripts/test_integrated_voice_management.py
```

### During Development
```bash
# Quick health check (30 seconds)
python scripts/test_core_examples.py --quick

# Link validation after doc changes
python scripts/check_links.py docs/api
```

### Implementation Phase Closing Protocol
```bash
# 1. Core functionality validation (2-3 minutes)
python scripts/test_core_examples.py

# 2. API synchronization check
python scripts/sync_openapi.py

# 3. Documentation integrity check
python scripts/check_links.py docs/api
```

### Major Releases / Documentation Updates
```bash
# Comprehensive validation (8-15 minutes total)
python scripts/test_curl_examples.py --timeout 90
python scripts/test_examples.py  
python scripts/check_links.py
python scripts/sync_openapi.py
```

### Troubleshooting
```bash
# Analyze examples without making requests (quick diagnosis)
python scripts/diagnose_curl_examples.py

# Check specific documentation paths
python scripts/check_links.py docs/api/endpoints/
```

## Requirements

### Environment
- Active Python virtual environment (`.venv`)
- Running API server at `http://localhost:7860`
- Required Python packages: `requests`, `pathlib`, `pydantic`

### For cURL/Generation Tests  
- **Audio files**: Ensure reference audio files exist for advanced examples
- **Timeouts**: Generation tests require adequate timeout values
- **Server state**: First request may take longer due to model loading

## Script Details

### test_core_examples.py
**Purpose**: Implementation protocol validation suite (Two-Tier Strategy Tier 1)  
**Features**: 
- Tests essential functionality in 2-3 minutes
- Universal compatibility (no specific voice file requirements)
- Uses existing project files only
- Progress indicators and clear pass/fail reporting
- Suitable for routine implementation phase validation

**Usage**:
```bash
python scripts/test_core_examples.py
python scripts/test_core_examples.py --quick  # Health check only
```

### test_working_examples.py
**Purpose**: Alternative core working examples validation  
**Features**:
- Quick validation of core working examples  
- Designed for routine validation (2-3 minutes)
- Avoids encoding issues and complex scenarios
- Suitable for implementation phase closing

**Usage**:
```bash
python scripts/test_working_examples.py
```

### test_curl_examples.py
**Purpose**: Comprehensive testing of all cURL examples (Two-Tier Strategy Tier 2)  
**Features**:
- Parses cURL commands from markdown documentation
- Converts to Python requests for testing
- Tests all documented examples (5 TTS + 3 VC generations)
- Requires 8-15 minutes for full run

**Usage**:
```bash
python scripts/test_curl_examples.py --timeout 90
python scripts/test_curl_examples.py --api-base http://localhost:8000
```
**Purpose**: Validates all internal markdown links in documentation  
**Features**: 
- Checks relative links between documentation files
- Validates anchor links within files
- Reports broken or missing references
- Supports filtering by directory

**Usage**:
```bash
python scripts/check_links.py [docs_path]
python scripts/check_links.py docs/api/endpoints/
```

### sync_openapi.py
**Purpose**: Ensures OpenAPI specification matches live API implementation  
**Features**:
- Compares file spec vs. live API endpoints
- Identifies missing or extra endpoints/schemas
- Reports version mismatches
- Supports strict mode (warnings as errors)

**Usage**:
```bash
python scripts/sync_openapi.py
python scripts/sync_openapi.py --strict
python scripts/sync_openapi.py --api-base http://localhost:8000
```

### test_examples.py  
**Purpose**: Validates Python code examples in documentation  
**Features**:
- Extracts Python code blocks from markdown files
- Tests examples against live API
- Reports syntax and runtime errors
- Focuses on Core API functionality

**Usage**:
```bash
python scripts/test_examples.py
python scripts/test_examples.py --docs-root docs/api/
```

### test_curl_examples.py
**Purpose**: Comprehensive testing of all cURL examples  
**Features**:
- Parses cURL commands from markdown documentation
- Converts to Python requests for testing
- Tests all documented examples (5 TTS + 3 VC generations)
- Requires 8-15 minutes for full run

**Usage**:
```bash
python scripts/test_curl_examples.py --timeout 90
python scripts/test_curl_examples.py --api-base http://localhost:8000
```

### test_working_examples.py
**Purpose**: Quick validation of core working examples  
**Features**:
- Tests essential functionality only (health, voices, outputs, 1 TTS)
- Designed for routine validation (2-3 minutes)
- Avoids encoding issues and complex scenarios
- Suitable for implementation phase closing

**Usage**:
```bash
python scripts/test_working_examples.py
```

### test_phase11_tts_reference_file_times_test.py
**Purpose**: Compare TTS generation times when using different reference voices  
**Features**:
- Tests TTS generation with multiple generations of the same text with same reference voice
- Uses the speed_factor parameter, generating the same audio at three different speeds
- Produces a written report in Markdown with configurable filename
- The tester can define different voice reference files for speed generation comparison of identical audio 

**Usage**:
```bash
python scripts/test_phase11_tts_reference_file_times_test.py
```

### test_integrated_tts_file_management.py
**Purpose**: Complete TTS output file management workflow validation  
**Features**:
- Tests TTS generation in organized project folders
- Validates file listing, searching, and folder structure operations
- Demonstrates complete file lifecycle: create → organize → find → delete
- Tests both individual file and bulk project folder deletion

**Usage**:
```bash
python scripts/test_integrated_tts_file_management.py
```

### test_integrated_vc_input_management.py
**Purpose**: Complete VC input file management workflow validation  
**Features**:
- Tests VC input file upload to organized project folders
- Validates file listing, searching, and folder structure operations
- Demonstrates complete upload lifecycle: upload → organize → find → delete
- Tests both individual file and bulk project folder deletion
- Auto-generates test files if insufficient media files available

**Usage**:
```bash
python scripts/test_integrated_vc_input_management.py
```

### test_integrated_voice_management.py
**Purpose**: Complete voice management workflow validation  
**Features**:
- Tests voice upload with metadata (name, description, tags, folders)
- Validates voice listing, searching by name/tags, and folder operations
- Demonstrates complete voice lifecycle: upload → organize → find → delete
- Tests voice categorization and metadata management
- Auto-generates voice samples if insufficient media files available

**Usage**:
```bash
python scripts/test_integrated_voice_management.py
```

### diagnose_curl_examples.py
**Purpose**: Analysis tool for troubleshooting cURL examples  
**Features**:
- Parses cURL commands without making requests
- Categorizes examples by type (TTS, VC, error demos)
- Identifies parsing issues and file reference problems
- Quick diagnostic tool (no API calls)

**Usage**:
```bash
python scripts/diagnose_curl_examples.py
```

## Future Enhancements

### Implemented (Two-Tier Testing Strategy)
- **test_core_examples.py**: Implementation protocol validation (2-3 minutes) ✅
- Enhanced categorization of examples (core vs. advanced) ✅  
- Two-tier validation strategy with clear usage guidelines ✅

### Planned
- Setup validation for required audio files
- Enhanced progress reporting and timing estimates
- Configuration options for different validation levels

### Integration Opportunities
- Pre-commit hooks for link validation
- CI/CD integration for automated testing
- Performance monitoring and timeout optimization

## Troubleshooting

### Common Issues
1. **Timeout errors**: Increase timeout values for generation endpoints
2. **Missing files**: Ensure required audio files exist for advanced examples  
3. **Server not running**: Start API server before running tests
4. **Encoding issues**: Scripts designed to avoid Unicode problems on Windows

### Getting Help
- Check script output for specific error details
- Use diagnostic scripts for analysis without API calls
- Verify server health with quick working examples test
- Review documentation for timeout and setup requirements

---

For detailed integration with documentation workflow, see: `docs/api/how-to-update-api-docs.md`

# Validation Scripts

This directory contains automated validation and testing scripts for the API documentation project.

## Script Overview

| Script | Purpose | Usage | Time |
|--------|---------|-------|------|
| **check_links.py** | Validates internal documentation links | `python scripts/check_links.py` | ~30 seconds |
| **sync_openapi.py** | Checks OpenAPI spec sync with live API | `python scripts/sync_openapi.py` | ~10 seconds |
| **test_examples.py** | Tests Python code examples in docs | `python scripts/test_examples.py` | ~60 seconds |
| **test_curl_examples.py** | Tests all cURL examples (comprehensive) | `python scripts/test_curl_examples.py --timeout 90` | ~8-15 minutes |
| **test_working_examples.py** | Tests core working examples only | `python scripts/test_working_examples.py` | ~2-3 minutes |
| **diagnose_curl_examples.py** | Analyzes cURL examples without requests | `python scripts/diagnose_curl_examples.py` | ~5 seconds |

## Usage by Scenario

### During Development
```bash
# Quick health check (30 seconds)
python scripts/test_working_examples.py

# Link validation after doc changes
python scripts/check_links.py docs/api
```

### Implementation Phase Closing
```bash
# Core functionality validation (2-3 minutes)
python scripts/test_working_examples.py

# API sync check
python scripts/sync_openapi.py

# Python examples validation
python scripts/test_examples.py
```

### Major Releases / Documentation Updates
```bash
# Comprehensive validation (8-15 minutes)
python scripts/test_curl_examples.py --timeout 90

# Full validation suite
python scripts/check_links.py
python scripts/sync_openapi.py  
python scripts/test_examples.py
```

### Troubleshooting
```bash
# Analyze cURL examples without making requests
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

### check_links.py
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

### Planned (Two-Tier Testing Strategy)
- **test_core_examples.py**: Implementation protocol validation (2-3 minutes)
- Enhanced categorization of examples (core vs. advanced)
- Setup validation for required audio files

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

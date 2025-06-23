# How to Update API Documentation

> **Chatterbox TTS Extended Plus** - Maintenance guide for API documentation

## Overview

This guide explains how to maintain and update the API documentation as the system evolves. It covers the modular structure, responsibilities, and procedures for keeping documentation accurate and useful.

## Documentation Structure

### Endpoint Classification System

The API documentation uses a two-tier classification system to organize endpoints by intended audience:

#### Core API Documentation
- **Target Audience**: End users, application developers, API integrators
- **Coverage**: Primary user-facing functionality
- **Documentation Location**: Main `openapi.yaml` + `endpoints/` directory
- **Endpoint Patterns**: `/tts`, `/vc`, `/voice*`, `/voices*`, `/outputs`, `/health`, `/config`

#### Administrative API Documentation  
- **Target Audience**: System administrators, DevOps teams, monitoring systems
- **Coverage**: System monitoring, resource management, cleanup, debugging
- **Documentation Location**: `reference/administrative-endpoints.md`
- **Endpoint Patterns**: `/metrics`, `/resources`, `/cleanup*`, `/errors*`

#### Classification Rules for New Endpoints
When adding new endpoints, classify them based on:

1. **Purpose**: User functionality (core) vs system management (administrative)
2. **Audience**: Application developers (core) vs system operators (administrative)
3. **URL Patterns**: 
   - Core: `/tts`, `/vc`, `/voice`, `/voices`, `/outputs`, `/health`, `/config`
   - Administrative: `/metrics`, `/resources`, `/cleanup`, `/errors`, `/admin`, `/debug`
4. **Response Models**: User-facing data (core) vs system metrics/status (administrative)

#### Future Automation Support
This classification is designed to support automated documentation maintenance:
- Endpoint detection by scanning `main_api.py`
- Automatic classification based on URL patterns and response models
- Separate documentation generation for core vs administrative endpoints

### File Organization

```
docs/api/
├── README.md                    # Navigation hub and overview
├── quick-start.md              # Getting started guide
├── how-to-update-api-docs.md   # This maintenance guide
├── endpoints/                  # Individual endpoint docs
│   ├── health.md              # /api/v1/health
│   ├── tts.md                 # /api/v1/tts
│   ├── voice-conversion.md    # /api/v1/vc
│   ├── voice-management.md    # /api/v1/voice*
│   └── file-operations.md     # /api/v1/outputs, etc.
├── guides/                     # Feature-specific guides
│   ├── streaming-responses.md # Response handling
│   ├── file-uploads.md        # Upload capabilities
│   ├── error-handling.md      # Error management
│   └── advanced-features.md   # Advanced functionality
├── schemas/                    # Data model documentation
│   ├── request-models.md      # API request schemas
│   ├── response-models.md     # API response schemas
│   └── examples/              # Code examples
│       ├── curl-examples.md   # cURL examples
│       └── python-examples.md # Python examples
├── reference/                  # Technical reference
│   ├── configuration.md       # Config file reference
│   ├── file-structure.md      # Directory structure
│   └── compatibility.md       # System requirements
└── openapi.yaml               # OpenAPI specification
```

### Responsibilities Matrix

| Component | Primary Responsibility | When to Update |
|-----------|----------------------|----------------|
| **endpoints/*.md** | API endpoint changes | New endpoints, parameter changes |
| **guides/*.md** | Feature additions | New features, workflow changes |
| **schemas/*.md** | Data model changes | Pydantic model updates |
| **reference/*.md** | System changes | Config options, requirements |
| **openapi.yaml** | API specification | Any API change |
| **README.md** | Navigation updates | Structure changes |

## Update Procedures

### 1. Adding New Endpoints

**Steps**:
1. **Create endpoint document** in `endpoints/`
2. **Update OpenAPI spec** in `openapi.yaml`
3. **Add examples** to `schemas/examples/`
4. **Update README navigation** links
5. **Test all examples** against running API

**Template for new endpoint**:
```markdown
# [Endpoint Name]

> **[HTTP Method]** `[endpoint path]` - Brief description

## Overview

[Purpose and functionality description]

## Request

### HTTP Method and URL
```
[METHOD] /api/v1/[path]
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param] | [type] | [yes/no] | [description] |

### Request Body
```json
{
  "example": "request"
}
```

## Response

### Success Response (200)
```json
{
  "success": true,
  "result": "data"
}
```

### Error Responses
[Standard error format documentation]

## Examples

### cURL
```bash
curl -X [METHOD] http://localhost:7860/api/v1/[path] \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}'
```

### Python
```python
import requests
# Example implementation
```

## See Also
- [Related docs links]
```

### 2. Updating Existing Endpoints

**When parameters change**:
1. **Update endpoint document** with new parameters
2. **Update OpenAPI spec** with new schema
3. **Update examples** to use new parameters
4. **Mark deprecated parameters** with warnings
5. **Update error handling** for new validation

**Parameter deprecation format**:
```markdown
| `old_param` | string | No | ⚠️ **DEPRECATED**: Use `new_param` instead |
```

### 3. Modifying Data Models

**When Pydantic models change**:
1. **Update schemas/request-models.md** or **response-models.md**
2. **Update validation rules** and constraints
3. **Add new examples** showing updated structure
4. **Update OpenAPI spec** with new schemas
5. **Update affected endpoint docs**

**Change tracking format**:
```markdown
### Field Changes (v1.1.0)
- **Added**: `new_field` - Description of new field
- **Modified**: `existing_field` - Now accepts additional values
- **Deprecated**: `old_field` - Will be removed in v2.0.0
```

### 4. Adding New Features

**For major features** (like audio concatenation):
1. **Create feature guide** in `guides/`
2. **Add endpoint documentation** if new endpoints
3. **Update advanced features** guide with examples
4. **Add examples** to appropriate collections
5. **Update quick start** if it affects basic usage

**For minor features** (like new parameters):
1. **Update relevant endpoint docs**
2. **Add examples** to existing collections
3. **Update configuration** reference if needed

## Validation Procedures

### 1. Example Testing

**Test all code examples**:
```bash
# Start the API server
python main_api.py

# Test cURL examples
./test_curl_examples.sh

# Test Python examples  
python test_python_examples.py
```

**Example testing script**:
```python
#!/usr/bin/env python3
"""Test all Python examples in documentation"""

import requests
import sys
import time

def test_basic_tts():
    """Test basic TTS example from quick-start.md"""
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json={"text": "Hello world"},
        stream=True
    )
    return response.status_code == 200

def test_all_examples():
    """Run all example tests"""
    tests = [
        test_basic_tts,
        # Add more test functions
    ]
    
    for test in tests:
        try:
            result = test()
            print(f"✓ {test.__name__}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")

if __name__ == "__main__":
    test_all_examples()
```

### 2. Link Validation

**Check internal links**:
```python
#!/usr/bin/env python3
"""Validate internal documentation links"""

import re
import os
from pathlib import Path

def check_markdown_links():
    """Check all relative links in markdown files"""
    docs_dir = Path("docs/api")
    broken_links = []
    
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        
        # Find relative links
        links = re.findall(r'\[.*?\]\(([^http][^)]+)\)', content)
        
        for link in links:
            # Remove anchor fragments
            link_path = link.split('#')[0]
            if link_path:
                target = (md_file.parent / link_path).resolve()
                if not target.exists():
                    broken_links.append(f"{md_file}: {link}")
    
    return broken_links

if __name__ == "__main__":
    broken = check_markdown_links()
    if broken:
        print("Broken links found:")
        for link in broken:
            print(f"  {link}")
        sys.exit(1)
    else:
        print("All links valid")
```

### 3. OpenAPI Synchronization

**Verify OpenAPI matches implementation**:
```python
#!/usr/bin/env python3
"""Check OpenAPI spec matches actual API"""

import requests
import yaml

def compare_openapi_with_api():
    """Compare OpenAPI spec with running API"""
    
    # Load OpenAPI spec
    with open("docs/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)
    
    # Test each endpoint
    base_url = "http://localhost:7860"
    
    for path, methods in spec["paths"].items():
        for method in methods.keys():
            if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                # Test if endpoint exists
                try:
                    response = requests.request(
                        method.upper(),
                        f"{base_url}{path}",
                        timeout=5
                    )
                    # 404 = endpoint missing, other codes = endpoint exists
                    if response.status_code == 404:
                        print(f"✗ Missing endpoint: {method.upper()} {path}")
                    else:
                        print(f"✓ Found endpoint: {method.upper()} {path}")
                except requests.exceptions.RequestException as e:
                    print(f"? Cannot test {method.upper()} {path}: {e}")

if __name__ == "__main__":
    compare_openapi_with_api()
```

## Change Impact Assessment

### Impact Matrix

| Change Type | Affected Files | Update Priority | Testing Required |
|-------------|---------------|-----------------|------------------|
| **New endpoint** | endpoint/, openapi.yaml, examples/ | High | Full API test |
| **Parameter change** | endpoint/, schemas/, openapi.yaml | High | Parameter validation |
| **New feature** | guides/, endpoint/, examples/ | Medium | Feature test |
| **Config change** | reference/configuration.md | Medium | Config validation |
| **Bug fix** | Specific files | Low | Targeted test |
| **Typo/format** | Specific files | Low | Visual review |

### Breaking Change Procedure

**For breaking changes**:
1. **Document in changelog** with migration guide
2. **Add deprecation warnings** to old documentation
3. **Create migration examples** showing before/after
4. **Update compatibility** reference with version info
5. **Coordinate with implementation** team on timeline

**Breaking change documentation**:
```markdown
## Breaking Changes in v2.0.0

### Removed Parameters
- **`old_parameter`**: Removed from TTS endpoint
  - **Migration**: Use `new_parameter` instead
  - **Example**: 
    ```json
    // Before (v1.x)
    {"old_parameter": "value"}
    
    // After (v2.0)  
    {"new_parameter": "value"}
    ```

### Changed Response Format
- **TTS Response**: `output_files` structure changed
  - **Migration**: Update response parsing logic
  - **See**: [Response Models](schemas/response-models.md#tts-response)
```

## Maintenance Schedule

### Regular Tasks

**Weekly**:
- Test all examples against latest API
- Check for broken internal links
- Review and update error handling examples

**Monthly**:
- Full OpenAPI synchronization check
- Update performance benchmarks
- Review and update troubleshooting guides

**Per Release**:
- Update version numbers
- Add changelog entries
- Test all integration examples
- Update compatibility requirements

### Automated Checks

**Pre-commit hooks**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-markdown-links
        name: Check markdown links
        entry: python scripts/check_links.py
        language: python
        files: ^docs/.*\.md$
      
      - id: test-api-examples
        name: Test API examples
        entry: python scripts/test_examples.py
        language: python
        files: ^docs/.*\.md$
```

**CI/CD integration**:
- Run link validation on PR
- Test examples on API changes
- Generate OpenAPI diff reports

## Quality Standards

### Documentation Standards

**Writing Style**:
- Clear, concise language
- Active voice preferred
- Code examples for all features
- Consistent terminology

**Structure Standards**:
- H1 for page title
- H2 for major sections  
- H3 for subsections
- Tables for parameter lists
- Code blocks with proper syntax highlighting

**Example Standards**:
- All examples must be tested
- Include both success and error cases
- Show realistic use cases
- Provide copy-pasteable code

## Endpoint Classification Procedures

### Adding New Core Endpoints
For endpoints intended for end users and application developers:

1. **Add to OpenAPI Specification**: Update `openapi.yaml` with full endpoint definition
2. **Create/Update Endpoint Documentation**: Add detailed docs in `endpoints/` directory
3. **Update Examples**: Add working examples to `schemas/examples/`
4. **Test Integration**: Verify Swagger UI generates correctly

### Adding New Administrative Endpoints
For endpoints intended for system administration and monitoring:

1. **Document in Administrative Reference**: Add to `reference/administrative-endpoints.md`
2. **Include Integration Examples**: Provide monitoring/automation examples
3. **Update README**: Add reference link if it's a new category
4. **Security Considerations**: Document access control recommendations

### Classification Decision Process
When uncertain about endpoint classification:

1. **Ask**: "Who is the primary user of this endpoint?"
   - Application developers → Core
   - System administrators → Administrative

2. **Consider**: "What type of data does this return?"
   - User-facing content → Core  
   - System metrics/status → Administrative

3. **Check URL Pattern**: Does it match existing patterns?
   - `/tts`, `/vc`, `/voice*` → Core
   - `/metrics`, `/cleanup*`, `/errors*` → Administrative

### Future Automation Readiness
When adding endpoints, structure them to support future automation:

- Use consistent URL patterns within classification
- Follow response model naming conventions (`*Response` for core, metric objects for admin)
- Include clear docstrings in `main_api.py`
- Use appropriate HTTP methods and status codes

### Version Control

**Commit Message Format**:
```
docs: [scope] brief description

Longer description if needed

- Specific changes made
- Files affected
- Testing performed
```

**Examples**:
```
docs: tts endpoint - add speed_factor parameter

Added documentation for new speed_factor parameter in TTS requests.

- Updated schemas/request-models.md with parameter details
- Added examples to endpoints/tts.md
- Updated openapi.yaml with new parameter
- Tested all examples against API v1.2.0
```

## See Also

- [API Docs Reorganization Plan](../../dev/api-docs-reorganization-plan.md) - Project structure
- [Configuration Reference](../reference/configuration.md) - System configuration
- [Compatibility Reference](../reference/compatibility.md) - Version requirements
- [Quick Start Guide](../quick-start.md) - Getting started

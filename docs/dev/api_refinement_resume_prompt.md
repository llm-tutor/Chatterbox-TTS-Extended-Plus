# Resume Development Prompt - API Refinement Project

## Context
I need to continue development of the **Chatterbox TTS Extended Plus API Refinement Project**. This is a systematic, phase-based project (Phases 9-14) to transform the existing FastAPI implementation from basic functionality into a production-ready, feature-rich API.

## Project Overview
- **Current State**: Look at the file `docs/dev/api_refinement_implementation_plan.md` to validate the completed and pending tasks.
- **Documentation State**: API Documentation Reorganization complete - Modular structure established
- **Goal**: Implement streaming responses, file uploads, enhanced metadata, speed control, voice management, audio concatenation, and OpenAI compatibility
- **Approach**: Incremental phases with detailed checklists, comprehensive testing, and validated documentation updates

## Instructions
Please read and analyze the following documents to understand the current project state and continue development:

### Essential Context Documents:
1. **Implementation Plan**: `docs/dev/api_refinement_implementation_plan.md` - Current phase status, task checklists, and next steps
2. **Conceptual Design**: Available in your project knowledge - Core design decisions and technical approach
3. **Change History**: `docs/changelog.md` - Complete implementation history and version tracking
4. **Current API Docs**: `docs/api/README.md` - Navigation hub for modular documentation structure
5. **Validation Scripts**: `scripts/README.md` - Complete testing and validation infrastructure

### Updated Documentation Structure:
The API documentation has been reorganized into a modular structure:

```
docs/api/
├── README.md                    # Navigation hub and overview
├── quick-start.md              # Getting started guide
├── endpoints/                  # Individual endpoint documentation
│   ├── health.md
│   ├── tts.md
│   ├── voice-conversion.md
│   ├── voice-management.md
│   └── file-operations.md
├── guides/                     # Feature-specific guides
│   ├── streaming-responses.md
│   ├── file-uploads.md
│   ├── error-handling.md
│   └── advanced-features.md
├── schemas/                    # Data models and examples
│   ├── request-models.md
│   ├── response-models.md
│   └── examples/
│       ├── curl-examples.md
│       ├── python-examples.md
│       └── ...
├── reference/                  # Technical reference
│   ├── configuration.md
│   ├── file-structure.md
│   └── compatibility.md
├── openapi.yaml               # OpenAPI specification (simplified but complete)
└── how-to-update-api-docs.md  # Maintenance guide
```

### Project Structure:
- **Working Directory**: `E:\Repos\Chatterbox-TTS-Extended-Plus`
- **Virtual Environment**: `.venv` (must be activated for all operations)

### Development Workflow:
1. **Read tracking document** to identify current phase and pending tasks
2. **Examine project structure** to understand current implementation state
3. **Complete phase tasks** following the detailed checklists in the implementation plan
4. **Update modular documentation** across relevant files as tasks are completed
5. **Run validation tests** using the two-tier testing strategy
6. **Test thoroughly** before marking tasks complete
7. **Prepare commit** with descriptive message when phase is finished

## Validation & Testing Strategy

### **Two-Tier Testing System** (Available)
The project uses a balanced testing approach for different scenarios:

#### **Tier 1: Core Validation (Implementation Protocol)**
**Purpose**: Quick validation during implementation phase closing  
**Time**: 2-3 minutes  
**Usage**: Routine development validation

```bash
# Core functionality validation (implementation protocol)
python scripts/test_working_examples.py

# Future: Core validation suite (when two-tier system is implemented)
python scripts/test_core_examples.py
```

#### **Tier 2: Comprehensive Validation (Release Quality)**
**Purpose**: Complete validation for releases and documentation updates  
**Time**: 8-15 minutes  
**Usage**: Major releases, documentation updates, comprehensive validation

```bash
# Comprehensive cURL examples test
python scripts/test_curl_examples.py --timeout 90

# Full validation suite
python scripts/check_links.py
python scripts/sync_openapi.py
python scripts/test_examples.py
```

### **Available Validation Scripts**
| Script | Purpose | Time | When to Use |
|--------|---------|------|-------------|
| `test_working_examples.py` | Core functionality | 2-3 min | Implementation protocol |
| `test_core_examples.py` | Core validation suite | 2-3 min | Implementation protocol (future) |
| `test_curl_examples.py` | Comprehensive cURL testing | 8-15 min | Releases, major changes |
| `test_examples.py` | Python code examples | ~1 min | Regular validation |
| `check_links.py` | Documentation links | ~30 sec | After doc changes |
| `sync_openapi.py` | API spec synchronization | ~10 sec | API endpoint changes |

> **📁 Complete documentation**: See `scripts/README.md` for detailed usage and troubleshooting

## Development Standards

### **Quality Requirements:**
- **Backward Compatibility**: Never break existing API functionality
- **Error Handling**: Comprehensive coverage using Phase 7 error tracking foundation
- **Resource Management**: Build on Phase 7 cleanup and monitoring systems
- **Testing**: Two-tier validation strategy for all new features
- **Documentation**: Immediate updates to relevant modular documentation files

### **Technical Guidelines:**
- **Build on Existing**: Leverage Phase 7 monitoring, resource management, and error handling
- **Reference Implementation**: Use Chatterbox-TTS-Server patterns for best practices
- **Incremental Approach**: Complete one phase fully before proceeding
- **Configuration**: Add new settings to `config.yaml` as needed
- **Metadata**: Implement consistent JSON companion files for all generated content

## Critical Implementation Instructions

### **Environment & Testing:**
- **Always activate venv**: Use `.venv` environment for all operations
- **Avoid launching server**: Request user to start server manually, then test via API calls
- **UTF-8 encoding**: Critical for Windows 11 Japanese encoding compatibility
- **No Unicode emojis in code output**: Avoid using in file's output due to encoding issues. It is not problem in itself, but you will see errors when trying to read the output.
- **Testing timeouts**: Use appropriate timeouts for generation endpoints (60-90 seconds)

### **Writing long files**
- A good idea for creating long files is to write them in chunks, instead of trying to write them in a single command.

### **Git & Documentation:**
- **PowerShell syntax**: Use full paths for all git commands
- **Incremental commits**: Completed-phase commits with clear, descriptive messages
- **OpenAPI updates**: Always update `docs/api/openapi.yaml` when modifying API endpoints
- **Modular doc updates**: Update relevant files in the modular structure (endpoints/, guides/, schemas/, reference/)
- **Phase completion**: Show commit message and wait for confirmation before executing
- It is not a bad idea to run first 'git status' or 'dir' to make sure you are in the right directory.

### **Documentation Update Protocol:**
When implementing new features, update the appropriate modular documentation files:

1. **New Endpoints**: Update or create files in `docs/api/endpoints/`
2. **New Features**: Update relevant guides in `docs/api/guides/`
3. **Request/Response Models**: Update `docs/api/schemas/request-models.md` and `response-models.md`
4. **Examples**: Update `docs/api/schemas/examples/curl-examples.md` and `python-examples.md`
5. **Configuration**: Update `docs/api/reference/configuration.md`
6. **OpenAPI Spec**: Update `docs/api/openapi.yaml`
7. **Navigation**: Update `docs/api/README.md` if adding new major sections

### **Phase Completion Protocol:**
Before marking a phase complete:

1. **Core Validation**: Run implementation protocol tests (2-3 minutes)
   ```bash
   python scripts/test_working_examples.py
   ```

2. **API Sync Check**: Verify OpenAPI spec matches implementation
   ```bash
   python scripts/sync_openapi.py
   ```

3. **Documentation Validation**: Check that doc updates are correct
   ```bash
   python scripts/check_links.py docs/api
   ```

4. **Feature-Specific Testing**: Test new functionality comprehensively

5. **For Major Releases**: Run comprehensive validation (8-15 minutes)
   ```bash
   python scripts/test_curl_examples.py --timeout 90
   python scripts/test_examples.py
   ```

### **Development Flow:**
- **One phase at a time**: Complete current phase fully before proceeding
- **Track progress**: Update `docs/dev/api_refinement_implementation_plan.md` as tasks complete
- **Test incrementally**: Use core validation for routine checks, comprehensive for releases
- **Update docs modularly**: Make targeted updates to relevant documentation files
- **Maintain compatibility**: Ensure existing functionality continues working
- **Wait after making a change**: When you make a change, the server reloads, so your first request may take longer. Take this into consideration for your tests. You may want to make a simple request and wait for its return, before making generative tests, as to avoid distortions about the response time due to the server loading.

## File Structure Reference

### **Key Implementation Files:**
```
main_api.py              # FastAPI application and endpoints
api_models.py            # Pydantic request/response models  
core_engine.py           # Core TTS/VC processing logic
utils.py                 # Utility functions and helpers
config.yaml              # Configuration settings
```

### **Modular Documentation Files:**
```
docs/api/README.md                          # Navigation hub
docs/api/quick-start.md                     # Getting started
docs/api/endpoints/*.md                     # Individual endpoint docs
docs/api/guides/*.md                        # Feature-specific guides
docs/api/schemas/*.md                       # Data models and examples
docs/api/reference/*.md                     # Technical reference
docs/api/openapi.yaml                       # OpenAPI specification
docs/api/how-to-update-api-docs.md         # Maintenance guide
docs/changelog.md                           # Version history
docs/dev/api_refinement_implementation_plan.md  # Phase tracking
```

### **Validation & Testing:**
```
scripts/README.md                           # Complete scripts documentation
scripts/test_working_examples.py           # Core validation (2-3 min)
scripts/test_core_examples.py              # Core validation suite (planned)
scripts/test_curl_examples.py              # Comprehensive testing (8-15 min)
scripts/test_examples.py                   # Python examples testing
scripts/check_links.py                     # Documentation link validation
scripts/sync_openapi.py                    # API spec synchronization
scripts/diagnose_curl_examples.py          # Troubleshooting tool
```

### **Directory Structure:**
```
reference_audio/         # Voice files for TTS and VC targets
vc_inputs/              # Source audio for voice conversion
outputs/                # Generated audio files
temp/                   # Temporary and download files
```

## Expected Response Pattern

**Phase Analysis:**
1. Read `docs/dev/api_refinement_implementation_plan.md` and `docs/changelog.md` to identify current phase and status
2. Examine relevant project files to understand current implementation state
3. Identify next specific task(s) from the phase checklist

**Implementation Approach:**
1. Begin with the next uncompleted task in the current phase
2. Implement changes following the design patterns established in previous phases
3. Update relevant modular documentation files as features are implemented
4. Test implementation using appropriate validation tier (core for routine, comprehensive for releases)
5. Update tracking document to mark tasks as complete
6. Update OpenAPI specification for any endpoint changes

**Completion Protocol:**
1. Run phase completion validation tests (core validation + API sync check)
2. When phase is complete, update `docs/changelog.md` and prepare comprehensive commit message
3. Wait for user confirmation before executing commit
4. Don't write files with the commit message, just present it in the chat for confirmation.
5. Provide summary of accomplished tasks and next phase preview

---

## Success Criteria
- **All phase tasks completed** according to implementation plan checklists
- **Comprehensive testing** using appropriate validation tier
- **Modular documentation updated** for all changes and new features
- **Backward compatibility** maintained throughout implementation
- **Production readiness** achieved through systematic quality standards
- **API specification synchronized** with implementation changes

## Integration with Two-Tier Testing Strategy

### **Development Workflow Integration:**
- **During development**: Use core validation for quick feedback
- **Phase completion**: Use core validation + API sync for closing protocol
- **Major releases**: Use comprehensive validation for complete coverage
- **Documentation changes**: Use link validation and example testing

### **Quality Assurance:**
- **Implementation protocol**: 2-3 minute validation ensures essential functionality
- **Release quality**: 8-15 minute comprehensive validation ensures complete coverage
- **Continuous validation**: Regular core testing maintains development velocity
- **Documentation quality**: Modular structure with targeted validation ensures maintainability

**Note**: This project transforms a basic API into a comprehensive, production-ready system with a modern, maintainable documentation structure and robust testing strategy. Maintain the systematic, quality-focused approach established in the previous 8 phases while leveraging the new modular documentation and two-tier testing infrastructure.

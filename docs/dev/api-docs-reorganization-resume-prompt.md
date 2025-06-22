# API Documentation Reorganization - Resume Prompt

## **Project Context**

I am working on reorganizing the API documentation for **Chatterbox TTS Extended Plus** project. The documentation has grown too large and unwieldy, and we are restructuring it into a modular, maintainable format.

### **Project Location**
- **Main Project**: `E:\Repos\Chatterbox-TTS-Extended-Plus`
- **Current Documentation**: `E:\Repos\Chatterbox-TTS-Extended-Plus\docs\api\`
- **Progress Tracking**: `E:\Repos\Chatterbox-TTS-Extended-Plus\docs\dev\api-docs-reorganization-plan.md`

### **Problem Statement**
The current API documentation consists of:
- **API_Documentation.md**: 915 lines (27.8KB) - Too large and monolithic
- **openapi.yaml**: 1,462 lines (45KB) - Extremely detailed but hard to navigate
- **Single-file approach**: Makes finding specific information difficult

### **Solution Approach**
Reorganizing into modular structure with:
- Quick start guides
- Individual endpoint documentation
- Feature-specific guides
- Schema and example collections
- Technical reference materials

## **Current Progress**

### **What Has Been Done**
Please check the progress tracking document at:
`E:\Repos\Chatterbox-TTS-Extended-Plus\docs\dev\api-docs-reorganization-plan.md`

Look for completed checkboxes [x] to see what tasks have been finished.

### **Key Constraints**
1. **Preserve all content**: No information should be lost during reorganization
2. **Maintain functionality**: Server `/docs` endpoint must continue working
3. **OpenAPI single file**: Keep `openapi.yaml` as single file for tool compatibility
4. **Backward compatibility**: All existing links and references must work
5. **Phase numbering clarity**: Always specify "API Docs reorganization Phase X" in changelog to avoid confusion with implementation phases

### **Important Considerations**
- **Multi-session project**: Context may be lost between sessions
- **Backup everything**: Keep `.backup` files until validation complete
- **Test examples**: All code samples must work with current API
- **Windows environment**: Use UTF-8 encoding, avoid Unicode emojis
- **Git workflow**: Commit changes in phases with descriptive messages

## **How to Resume**

### **Step 1: Check Current Status**
```bash
# Read the progress tracking document
desktop-commander:read_file docs/dev/api-docs-reorganization-plan.md
```

### **Step 2: Identify Next Tasks**
Look for the **"Current Status"** section and **"Next Task"** indicated in the plan.

### **Step 3: Verify Environment**
```bash
# Check current directory structure
desktop-commander:list_directory E:\Repos\Chatterbox-TTS-Extended-Plus\docs\api

# Activate virtual environment if needed for testing
# .venv environment is located in the project root
```

### **Step 4: Continue Implementation**
Follow the checklist items in the order specified in the plan document.

## **Key Files to Reference**

### **Original Documentation (for extraction)**
- `docs/api/API_Documentation.md` - Main documentation file
- `docs/api/openapi.yaml` - OpenAPI specification
- `docs/api/api_testing_guide.md` - Testing examples
- `docs/api/README.md` - Current overview

### **Project Implementation (for validation)**
- `main_api.py` - Main FastAPI application
- `api_models.py` - Pydantic request/response models
- `core_engine.py` - Core TTS/VC functionality
- `utils.py` - Utility functions

### **Configuration and Structure**
- `config.yaml` - Application configuration
- `docs/dev/api_refinement_implementation_plan.md` - Implementation phases
- Audio file structure document (in project knowledge)

## **Development Guidelines**

### **Environment & Documentation**
- **UTF-8 encoding**: Critical for Windows 11 Japanese encoding compatibility
- **No Unicode emojis**: Avoid in output due to encoding issues
- Always use absolute paths starting with `E:\Repos\Chatterbox-TTS-Extended-Plus`
- Chunk large files into ≤30 line pieces for optimal performance

### **Git & Documentation Workflow**
- **PowerShell syntax**: Use full paths for all git commands
- **Incremental commits**: Complete-phase commits with clear, descriptive messages
- **Phase completion protocol**: 
  1. Update `docs/changelog.md` with completed work
  2. Show commit message and wait for user confirmation
  3. Don't write files with commit message, present in chat for approval
- **Progress tracking**: Always update `api-docs-reorganization-plan.md` as tasks complete

### **Documentation-Specific Rules**
- **One phase at a time**: Complete current phase fully before proceeding
- **Preserve all functionality**: Test that existing links and references work
- **Cross-reference validation**: Verify all internal documentation links
- **Content preservation**: No information loss during reorganization

## **Common Commands**

### **Reading Progress**
```bash
desktop-commander:read_file docs/dev/api-docs-reorganization-plan.md
```

### **Checking File Structure**
```bash
desktop-commander:list_directory docs/api
```

### **Creating New Documentation Files**
```bash
desktop-commander:write_file path/to/new/file.md "content"
```

### **Backing Up Files**
```bash
desktop-commander:move_file original.md original.md.backup
```

## **Success Indicators**

### **Phase Completion**
- All checkboxes in current phase marked [x]
- New files created and populated with relevant content
- Cross-references updated to point to new structure
- Examples tested and validated

### **Session End Criteria**
- Clear stopping point identified in plan
- Progress documented in tracking file
- Any intermediate work committed to git
- Next session starting point clearly defined

## **Emergency References**

### **If Implementation Details Are Unclear**
Check the conceptual design documents in project knowledge:
- 'api_refinement_conceptual_design.md' - Overall design philosophy
- 'audio_files_directory_structure.md' - File organization patterns

### **If API Behavior Is Unclear**
Reference the working implementation in:
- `E:\Repos\Chatterbox-TTS-Server` - Working FastAPI reference
- Current `main_api.py` - Live implementation

### **If Unsure About Content Organization**
Examine current content structure:
```bash
desktop-commander:search_code docs/api/API_Documentation.md "^#+ .*"
```

This will show the current heading structure to guide reorganization decisions.

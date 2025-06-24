# Two-Tier Testing Strategy Implementation - Resume Prompt

## **Project Context**

I am working on implementing the **Two-Tier Testing Strategy** for **Chatterbox TTS Extended Plus** project. This follows the successful completion of the API Documentation Reorganization project and aims to create a balanced testing approach for development workflow efficiency.

### **Project Location**
- **Main Project**: `E:\Repos\Chatterbox-TTS-Extended-Plus`
- **Strategy Document**: `E:\Repos\Chatterbox-TTS-Extended-Plus\docs\dev\two-tier-testing-strategy.md`
- **Progress Tracking**: `E:\Repos\Chatterbox-TTS-Extended-Plus\docs\dev\two-tier-testing-implementation-plan.md`
- **Scripts Directory**: `E:\Repos\Chatterbox-TTS-Extended-Plus\scripts\`

### **Problem Statement**
Current comprehensive cURL testing requires **8-15 minutes** (5 TTS + 3 VC generations), which is impractical for routine implementation phase validation but necessary for complete documentation coverage.

### **Solution Overview**
Implement a **two-tier testing approach**:
- **Tier 1: Core Validation** (2-3 minutes) - Implementation protocol
- **Tier 2: Comprehensive Documentation** (8-15 minutes) - Full coverage for releases

## **Prerequisites Completed**

### **✅ API Documentation Reorganization (COMPLETED)**
- All 4 phases completed and committed (`41cf02b`)
- Modular documentation structure established
- Validation scripts created and documented
- cURL examples updated with real file references

### **✅ Current Validation Infrastructure**
- **6 validation scripts** documented in `scripts/README.md`
- **Workflow integration** established in `docs/api/how-to-update-api-docs.md`
- **JSON parsing fixed** in cURL testing scripts
- **Working examples validated** with proper timeouts

## **Current Progress**

### **What Has Been Done**
Check the progress tracking document at:
`E:\Repos\Chatterbox-TTS-Extended-Plus\docs\dev\two-tier-testing-implementation-plan.md`

Look for completed checkboxes [x] to see what tasks have been finished.

### **Key Design Decisions**

#### **Core Examples Strategy**
- **TTS Core Example**: WITHOUT reference voice (universal compatibility)
- **VC Core Example**: Using existing project files only
- **Advanced Examples**: Require specific voice files with setup documentation

#### **File Requirements Documentation**
- **Core examples**: Work universally without specific voice file requirements
- **Advanced examples**: Require clear documentation of voice file setup
- **Setup validation**: Developers can verify available voices before running examples

## **How to Resume**

### **Step 1: Check Current Status**
```bash
# Read the progress tracking document
desktop-commander:read_file docs/dev/two-tier-testing-implementation-plan.md
```

### **Step 2: Identify Next Tasks**
Look for the **"Current Status"** section and **"Next Task"** indicated in the plan.

### **Step 3: Verify Environment**
```bash
# Check current scripts directory
desktop-commander:list_directory E:\Repos\Chatterbox-TTS-Extended-Plus\scripts

# Activate virtual environment if needed for testing
# .venv environment is located in the project root
```

### **Step 4: Continue Implementation**
Follow the checklist items in the order specified in the implementation plan document.

## **Key Files to Reference**

### **Strategy and Planning**
- `docs/dev/two-tier-testing-strategy.md` - Original detailed strategy (reference only)
- `docs/dev/two-tier-testing-implementation-plan.md` - Trackable implementation checklist
- `scripts/README.md` - Current scripts documentation

### **Current Documentation Structure (Established)**
- `docs/api/schemas/examples/curl-examples.md` - Examples to be reorganized
- `docs/api/how-to-update-api-docs.md` - Workflow integration to be updated
- `docs/api/quick-start.md` - May need setup documentation updates

### **Current Scripts (Reference Implementation)**
- `scripts/test_curl_examples.py` - Comprehensive tester (8-15 min)
- `scripts/test_working_examples.py` - Core functionality tester (2-3 min)
- `scripts/diagnose_curl_examples.py` - Troubleshooting tool
- Other validation scripts (check `scripts/README.md`)

### **Audio Files for Testing**
- `reference_audio/test_voices/linda_johnson_01.mp3` - Reference voice
- `reference_audio/test_voices/linda_johnson_02.mp3` - Available voice
- `vc_inputs/test_inputs/chatterbox-hello_quick_brown.wav` - For VC testing
- `vc_inputs/test_inputs/chatterbox-in-a-village-of-la-mancha.mp3` - Additional VC input file

## **Development Guidelines**

### **Environment & Testing**
- **UTF-8 encoding**: Critical for Windows 11 Japanese encoding compatibility
- **No Unicode emojis**: Avoid in output due to encoding issues
- **Testing timeouts**: 60 seconds for core validation, 90 seconds for comprehensive
- **Server considerations**: First request after reload takes longer (model loading)

### **Script Development**
- **Core validation target**: 2-3 minutes maximum
- **Universal compatibility**: Core examples must work without specific voice files
- **Clear error messages**: Distinguish between setup issues and API problems
- **Encoding safety**: Test scripts must handle Windows Japanese encoding

### **Documentation Requirements**
- **Setup requirements**: Clear documentation for advanced examples
- **File prerequisites**: Document required audio files for each tier
- **Usage scenarios**: When to use core vs comprehensive validation
- **Integration guidance**: How scripts fit into implementation workflow

## **Implementation Strategy**

### **Tier 1: Core Validation (Implementation Protocol)**
**Target**: 2-3 minutes maximum
**Examples**:
```python
core_tests = [
    ("Health Check", "GET", "/api/v1/health"),
    ("List Voices", "GET", "/api/v1/voices"), 
    ("List Outputs", "GET", "/api/v1/outputs"),
    ("Basic TTS", "POST", "/api/v1/tts", {
        "text": "Hello, this is a core validation test.",
        "export_formats": ["wav"]
    }),
    ("Basic VC", "POST", "/api/v1/vc", {
        "input_audio_source": "test_inputs/chatterbox-hello_quick_brown.wav",
        "target_voice_source": "test_voices/linda_johnson_01.mp3",
        "export_formats": ["wav"]
    })
]
```

### **Tier 2: Comprehensive Documentation**
**Target**: 8-15 minutes (acceptable for thorough validation)
**Coverage**: All current examples with proper setup documentation

## **Common Commands**

### **Reading Progress**
```bash
desktop-commander:read_file docs/dev/two-tier-testing-implementation-plan.md
```

### **Testing Current Scripts**
```bash
# Quick core functionality test
python scripts/test_working_examples.py

# Comprehensive validation
python scripts/test_curl_examples.py --timeout 90

# Troubleshooting
python scripts/diagnose_curl_examples.py
```

### **Creating New Scripts**
```bash
desktop-commander:write_file scripts/test_core_examples.py "content"
```

### **Git Operations**
```bash
cd "E:\Repos\Chatterbox-TTS-Extended-Plus"; git status
cd "E:\Repos\Chatterbox-TTS-Extended-Plus"; git add . && git commit -m "message"
```

## **Success Indicators**

### **Core Validation (Tier 1)**
- Completes in 2-3 minutes consistently
- Works universally without specific voice file requirements
- Tests essential functionality: health, TTS generation, VC, endpoints
- Suitable for implementation phase closing protocol

### **Comprehensive Validation (Tier 2)**
- Covers all documented examples
- Advanced examples work with proper setup
- Clear documentation of requirements and setup
- Suitable for releases and developer onboarding

### **Documentation Quality**
- Clear separation between core and advanced examples
- Setup requirements clearly documented
- Integration with implementation workflow established
- Scripts properly documented and maintainable

## **Emergency References**

### **If Strategy Details Are Unclear**
Check the original strategy document:
```bash
desktop-commander:read_file docs/dev/two-tier-testing-strategy.md
```

### **If Current Scripts Behavior Is Unclear**
Check comprehensive scripts documentation:
```bash
desktop-commander:read_file scripts/README.md
```

### **If Integration Points Are Unclear**
Check maintenance guide:
```bash
desktop-commander:read_file docs/api/how-to-update-api-docs.md
```

## **Session End Criteria**

### **Phase Completion**
- All checkboxes in current phase marked [x] in implementation plan
- New scripts created and tested successfully
- Documentation updated to reflect changes
- Integration with workflow validated

### **Project Completion**
- Both tiers implemented and working
- Documentation reorganized with clear separation
- Scripts integrated into development workflow
- Validation strategy ready for routine use

---

**Note**: This implementation builds on the successfully completed API Documentation Reorganization project. All foundational work (modular structure, validation scripts, documentation) is already in place and ready for enhancement.

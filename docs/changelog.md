# Changelog - Chatterbox TTS Extended Plus API Implementation

All notable changes to the API implementation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Ready for Next Phase
- **Phase 6: Polish & Production** ready to begin
- All Gradio integration completed and validated

---

## [1.4.0] - 2025-06-18

### Added
- **Complete Gradio Integration** with FastAPI mounting at `/ui` endpoint
- **`create_interface()` function** in Chatter.py for reusable Gradio interface creation
- **FastAPI integration support** with backward compatibility in Chatter.py
- **Seamless UI/API coexistence** - both interfaces work independently
- **Comprehensive Phase 5 testing** with integration validation
- **Unicode compatibility fixes** for cross-platform Windows support

### Changed
- **Modified Chatter.py** to support both standalone and FastAPI integration modes
- **Enhanced main_api.py** with complete Gradio mounting functionality
- **Improved project structure** with proper separation of concerns
- **Updated application lifecycle** to handle both UI and API components

### Fixed
- **Unicode encoding issues** removed problematic Unicode characters for Windows compatibility
- **Import path handling** for proper module resolution in integration mode
- **Application mounting** proper Gradio app mounting in FastAPI

### Tested
- **✅ Module Import Tests:** All imports working correctly (Chatter, main_api)
- **✅ Interface Creation:** Gradio interface creation working properly
- **✅ FastAPI Integration:** All API routes registered and accessible
- **✅ UI Mounting:** Gradio UI successfully mounted at `/ui` endpoint
- **✅ Backward Compatibility:** Chatter.py still works standalone
- **✅ Both Interfaces:** API and UI working independently and together

### Technical Implementation
- **Gradio Integration:** UI mounted at `/ui` with full functionality preserved
- **API Endpoints:** All Phase 4 API endpoints remain fully functional
- **Configuration:** UI mounting controlled by `ui.enable_ui` config setting
- **Error Handling:** Graceful degradation if UI mounting fails

### Notes
- **Phase 5 Completed:** Full Gradio integration implemented and tested
- **2/2 Integration Tests Passing:** All Phase 5 tests successful
- **Production Ready:** Both API and UI working seamlessly together
- **Next Phase:** Ready for Phase 6 - Polish & Production
- **Access Instructions:**
  - API: `http://localhost:7860/api/v1/*` 
  - UI: `http://localhost:7860/ui`
  - Server: `python main_api.py`

---

## [1.3.0] - 2025-06-18

### Added
- **Enhanced URL validation** with safety checks for localhost/private IP blocking
- **File path sanitization** to prevent directory traversal attacks
- **Enhanced text input validation** with control character removal and length limits
- **URL download functionality** with safety validation in core engine
- **Comprehensive input sanitization** across all API models
- **Enhanced error handling** with detailed validation error responses
- **Security features** for safe file and URL handling

### Changed
- **Updated Pydantic models** to use `model_dump()` instead of deprecated `dict()`
- **Enhanced API validation** with automatic input sanitization
- **Improved error responses** with better structure and details
- **Cross-platform path handling** for consistent file operations

### Fixed
- **Pydantic deprecation warnings** by updating to model_dump()
- **URL validation security** now properly blocks dangerous URLs
- **File path security** with sanitization and traversal prevention
- **Text input security** with control character filtering

### Tested
- **✅ Enhanced URL Validation:** All URL safety checks working correctly
- **✅ File Path Sanitization:** Directory traversal prevention working
- **✅ Text Input Validation:** Control character removal and length limits working
- **✅ Pydantic Model Validation:** Input sanitization working across all models
- **✅ Error Response Format:** New model_dump format working correctly
- **✅ All Phase 4 Tests:** 5/5 enhanced feature tests passing

### Security
- **URL safety validation** prevents access to localhost and private IP ranges
- **File path sanitization** prevents directory traversal attacks
- **Text input validation** removes potentially harmful control characters
- **Input sanitization** across all API endpoints

### Notes
- **Phase 4 Completed:** All enhanced features implemented, tested, and validated
- **Security Enhanced:** Comprehensive input validation and sanitization
- **API Hardened:** Protection against common web security vulnerabilities
- **Next Phase:** Ready for Phase 5 - Gradio Integration
- **Testing:** All existing functionality preserved and enhanced

---

## [1.2.0] - 2025-06-18

### Added
- Complete FastAPI application (`main_api.py`) with all core endpoints
- TTS endpoint: `POST /api/v1/tts` with full parameter support
- VC endpoint: `POST /api/v1/vc` with audio source handling
- Health check endpoint: `GET /api/v1/health`
- Configuration endpoint: `GET /api/v1/config`
- Voice listing endpoint: `GET /api/v1/voices`
- Static file serving for outputs at `/outputs/`
- Comprehensive error handling with custom exception mapping
- CORS middleware for local development
- Application lifespan management (startup/shutdown)
- Basic API testing script (`test_api_basic.py`)

### Changed
- Project ready for live API testing
- Directory structure validated and working
- All imports functioning correctly

### Fixed
- Unicode character issues in testing scripts
- Configuration loading working properly
- CUDA device detection functional
- **TTS parameter passing issue:** Fixed duplicate parameter error in core engine
- **Core functionality validated:** TTS and VC working with real audio files

### Tested
- **✅ API Server:** Successfully running on localhost:7860
- **✅ All Endpoints:** Health, Config, Voices, TTS, VC all responding correctly
- **✅ TTS Generation:** Working with reference audio files
- **✅ VC Processing:** Working with input and target audio files
- **✅ Error Handling:** Proper error responses for missing files
- **✅ Multi-format Output:** WAV, MP3 conversion working

### Notes
- **Phase 3 Completed:** All basic API endpoints implemented and tested
- **Manual Testing Completed:** API server tested with real audio files
- **Next Phase:** Ready for Phase 4 - Enhanced Features
- **Testing Command:** `python main_api.py` to start server on localhost:7860
- **All Core Functionality Validated:** TTS, VC, and utility endpoints working correctly

---

## [1.1.0] - 2025-06-18

### Added
- Complete `core_engine.py` with CoreEngine class
- TTS generation logic extracted from Chatter.py
- VC generation logic extracted from Chatter.py
- Model loading and device management
- Audio file download functionality for URLs
- Audio format conversion utilities
- Text preprocessing methods
- Temporary file cleanup management

### Changed
- Project ready for API endpoint implementation

### Fixed
- Virtual environment dependencies properly installed
- Import structure working correctly

### Notes
- **Phase 2 Completed:** Core logic extraction finished successfully
- **Next Phase:** Ready to implement FastAPI endpoints
- **Testing:** CoreEngine import and basic functionality validated

---

## [1.0.1] - 2025-06-18

### Added
- Complete configuration management system (`config.py`, `config.yaml`)
- Custom exception hierarchy (`exceptions.py`) 
- Utility functions (`utils.py`)
- API request/response models (`api_models.py`)
- Project directory structure (logs/, reference_audio/, vc_inputs/, outputs/, temp/)
- FastAPI dependencies added to requirements.txt

### Changed
- Project structure now ready for core logic extraction

### Fixed
- Configuration loading and device detection working properly

### Notes
- **Phase 1 Completed:** All setup and configuration tasks finished
- **Next Phase:** Ready to begin core logic extraction from Chatter.py
- **Testing:** Configuration system validated and operational

---

## [1.0.0] - 2025-06-18

### Added
- Initial project setup for API implementation
- Created `docs/implementation_tracking.md` for phase tracking
- Created `docs/changelog.md` for change documentation
- Established development workflow based on implementation plan v1.1

### Changed
- Initiated transition from JSON-based settings to YAML configuration
- Started migration from Gradio-only to FastAPI + Gradio architecture

### Notes
- **Phase 1 Started:** Setup & Configuration phase begun
- **Reference Implementation:** Using Chatterbox-TTS-Server as configuration model
- **Target Architecture:** FastAPI main app with Gradio UI mounted at /ui

---

## Development Notes

### Version Numbering
- **Major:** Significant architectural changes (e.g., API introduction)
- **Minor:** New features or endpoints
- **Patch:** Bug fixes and minor improvements

### Phase Milestones
Each implementation phase will be marked with a version increment:
- Phase 1 (Setup): v1.0.x
- Phase 2 (Core Logic): v1.1.x  
- Phase 3 (Basic API): v1.2.x
- Phase 4 (Enhanced Features): v1.3.x
- Phase 5 (Gradio Integration): v1.4.x
- Phase 6 (Polish): v1.5.x

### Change Categories
- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

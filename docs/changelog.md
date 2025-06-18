# Changelog - Chatterbox TTS Extended Plus API Implementation

All notable changes to the API implementation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Initial CoreEngine class with BASIC TTS and VC logic extraction
- Audio file download support for URLs
- Multi-format audio conversion (WAV, MP3, FLAC)
- Comprehensive file resolution logic

### Changed
- Ready to begin Phase 3: Basic API Implementation

### In Progress
- Preparing to implement FastAPI endpoints

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

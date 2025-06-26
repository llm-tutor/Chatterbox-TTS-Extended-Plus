# File Structure Reference

> **Chatterbox TTS Extended Plus** - Directory organization and file management

## Overview

This document describes the complete file structure of the Chatterbox TTS system, including directory purposes, file organization patterns, and best practices for file management.

## Project Directory Structure

```
Chatterbox-TTS-Extended-Plus/
├── config.yaml                     # Main configuration file
├── main_api.py                     # FastAPI application entry point
├── core_engine.py                  # Core TTS/VC functionality
├── api_models.py                   # Pydantic request/response models
├── utils/                          # Modular utility functions
│   ├── __init__.py                 # Module imports and organization
│   ├── audio/                      # Audio processing utilities
│   │   ├── __init__.py
│   │   ├── processing.py           # Speed factor, duration calculation
│   │   ├── analysis.py             # Format normalization, silence detection
│   │   └── trimming.py             # Audio trimming functions
│   ├── concatenation/              # Audio concatenation utilities
│   │   ├── __init__.py
│   │   ├── parsing.py              # Parse concat instructions
│   │   ├── basic.py                # Basic concatenation
│   │   └── advanced.py             # Advanced concatenation
│   ├── files/                      # File operation utilities
│   │   ├── __init__.py
│   │   ├── naming.py               # Filename generation and sanitization
│   │   └── operations.py           # File validation and management
│   ├── voice/                      # Voice management utilities
│   │   ├── __init__.py
│   │   ├── metadata.py             # Voice metadata operations
│   │   ├── management.py           # Voice file management
│   │   └── organization.py         # Voice folder structure
│   ├── outputs/                    # Output file utilities
│   │   ├── __init__.py
│   │   └── management.py           # Generation metadata and file scanning
│   ├── validation/                 # Input validation utilities
│   │   ├── __init__.py
│   │   ├── text.py                 # Text validation
│   │   ├── audio.py                # Audio format validation
│   │   └── network.py              # URL validation
│   └── formatting/                 # Display formatting utilities
│       ├── __init__.py
│       └── display.py              # File size formatting
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (optional)
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
├── models/                        # AI model files
│   ├── tts/                      # Text-to-speech models
│   └── vc/                       # Voice conversion models
├── reference_audio/               # Reference voice files (all types)
│   ├── tts_voices/               # TTS-specific reference voices
│   ├── vc_targets/               # VC target voices
│   └── shared/                   # Voices used for both TTS and VC
├── vc_inputs/                     # Source audio files for voice conversion
│   ├── meeting_recordings/       # Organized by category
│   ├── podcasts/
│   └── personal/
├── outputs/                       # Generated audio files
│   ├── tts_YYYY-MM-DD_HHMMSS_*.wav
│   ├── vc_YYYY-MM-DD_HHMMSS_*.wav
│   └── *.json                    # Metadata files
├── temp/                          # Temporary files and downloads
│   ├── download_*.wav            # Downloaded from URLs
│   └── processing_*.wav          # Temporary processing files
├── logs/                          # Application logs
├── docs/                          # Documentation (this structure)
│   ├── api/                      # API documentation
│   └── dev/                      # Development documentation
└── tests/                         # Test files
```

## Audio File Directories

### reference_audio/ - Reference Voice Files

**Purpose**: Store all reference voices used for TTS generation and VC targets.

**Structure**:
```
reference_audio/
├── tts_voices/                    # TTS-specific reference voices
│   ├── narrator_formal.wav
│   ├── speaker1_casual.wav
│   └── presenter_energetic.wav
├── vc_targets/                    # Voice conversion target voices
│   ├── celebrity_voice.wav
│   ├── custom_character.wav
│   └── professional_speaker.wav
├── shared/                        # Voices used for both TTS and VC
│   ├── main_character.wav
│   └── brand_voice.wav
└── categories/                    # Organized by type
    ├── business/
    │   ├── ceo_voice.wav
    │   └── presenter.wav
    ├── entertainment/
    │   ├── comedian.wav
    │   └── announcer.wav
    └── characters/
        ├── hero.wav
        └── villain.wav
```

**File Requirements**:
- **Formats**: WAV (preferred), MP3, FLAC
- **Duration**: 5-30 seconds recommended
- **Quality**: 22050 Hz sample rate minimum
- **Content**: Clear speech, minimal background noise

### vc_inputs/ - Voice Conversion Source Audio

**Purpose**: Store source audio files to be converted using voice conversion.

**Structure**:
```
vc_inputs/
├── meeting_recordings/
│   ├── team_call_2024.wav
│   └── client_presentation.mp3
├── podcasts/
│   ├── episode_01.wav
│   └── interview_raw.wav
├── personal/
│   ├── speech_practice.wav
│   └── voicemail.mp3
└── projects/
    ├── audiobook_chapters/
    │   ├── chapter_01.wav
    │   └── chapter_02.wav
    └── voice_training/
        ├── exercise_01.wav
        └── exercise_02.wav
```

**Organization Tips**:
- Group by project or source type
- Use descriptive folder names
- Include date in filenames when relevant
- Keep original files as backup

### outputs/ - Generated Audio Files

**Purpose**: Store all generated audio files from TTS, VC, and concatenation operations.

**Naming Convention**:
```
{operation}_{timestamp}_{microseconds}_{parameters}.{format}

Examples:
tts_2025-06-22_143022_456_temp0.75_seed42.wav
vc_2025-06-22_143045_789_chunk60_overlap0.1.wav
concat_2025-06-22_143100_123_3files_leveled.wav
```

**Metadata Files**:
Each generated audio file has an accompanying JSON metadata file:
```
tts_2025-06-22_143022_456_temp0.75_seed42.json
```

**Cleanup Strategy**:
```
outputs/
├── 2025-06-22/              # Organized by date
│   ├── tts_*.wav
│   ├── vc_*.wav
│   └── *.json
├── 2025-06-21/
└── archive/                 # Older files moved here
```

### temp/ - Temporary Files

**Purpose**: Store temporary files during processing and downloads from URLs.

**Structure**:
```
temp/
├── download_12345.wav          # Downloaded from URL
├── processing_chunk_1.wav      # Temporary processing files
├── upload_abc123.wav           # Uploaded files before processing
└── cleanup_queue/              # Files scheduled for deletion
    ├── old_temp_1.wav
    └── old_temp_2.wav
```

**Automatic Cleanup**:
- Files older than 24 hours are automatically removed
- Failed downloads are cleaned up immediately
- Processing temp files removed after successful completion

## File Resolution Logic

### API File Resolution

The API resolves files using this priority order:

1. **Direct path match** in appropriate directory
2. **Filename with extensions** (.wav, .mp3, .flac)
3. **Subdirectory search** within appropriate base directory
4. **URL download** if source starts with http:// or https://

### Example Resolution Process

**TTS Reference Audio**:
```python
# Request: {"reference_audio_filename": "speaker1"}
# Resolution order:
1. reference_audio/speaker1
2. reference_audio/speaker1.wav
3. reference_audio/speaker1.mp3  
4. reference_audio/tts_voices/speaker1.wav
5. reference_audio/shared/speaker1.wav
# ... continue in all subdirectories
```

**VC Input Audio**:
```python
# Request: {"input_audio_source": "meeting"}
# Resolution order:
1. vc_inputs/meeting
2. vc_inputs/meeting.wav
3. vc_inputs/meeting.mp3
4. vc_inputs/meeting_recordings/meeting.wav
# ... continue in all subdirectories
```

## File Management Best Practices

### Organization Strategies

**By Purpose**:
```
reference_audio/
├── tts/           # TTS-only voices
├── vc/            # VC-only targets  
└── shared/        # Used for both
```

**By Category**:
```
reference_audio/
├── business/      # Professional voices
├── entertainment/ # Creative voices
└── personal/      # Custom voices
```

**By Quality**:
```
reference_audio/
├── studio/        # High-quality recordings
├── good/          # Good quality
└── experimental/  # Test voices
```

### Naming Conventions

**Reference Voices**:
```
{purpose}_{quality}_{description}.wav

Examples:
narrator_studio_professional.wav
presenter_good_energetic.wav
character_experimental_villain.wav
```

**Source Audio**:
```
{project}_{date}_{description}.wav

Examples:
meeting_2025-06-22_team-standup.wav
podcast_2025-06-20_interview-ceo.wav
training_2025-06-19_voice-exercise.wav
```

### Metadata Management

**Voice Metadata Files**:
```json
// speaker1.wav.json
{
  "name": "Professional Speaker 1",
  "description": "Clear, authoritative business voice",
  "duration_seconds": 12.5,
  "sample_rate": 22050,
  "file_size_bytes": 276480,
  "format": "wav",
  "tags": ["professional", "business", "clear"],
  "created_date": "2025-06-20T10:00:00Z",
  "usage_count": 15,
  "default_parameters": {
    "temperature": 0.8,
    "speed_factor": 1.1
  }
}
```

## Storage and Backup

### Disk Space Management

**Estimated Storage Requirements**:
- **Reference voices**: 50-100 voices × 1-5MB = 50-500MB
- **Generated outputs**: 100-500 files × 1-10MB = 100MB-5GB
- **Models**: TTS + VC models = 1-5GB
- **Temporary files**: 100-500MB (auto-cleaned)

**Total**: 2-10GB for typical installation

### Backup Strategy

**Critical Files** (must backup):
```
config.yaml
reference_audio/
models/ (if custom-trained)
```

**Important Files** (should backup):
```
vc_inputs/ (if not backed up elsewhere)
outputs/ (recent generations)
```

**Temporary Files** (no backup needed):
```
temp/
logs/
```

### Archive Strategy

**Automatic Archival**:
```python
# Example archival script
def archive_old_outputs():
    cutoff_date = datetime.now() - timedelta(days=30)
    for file in outputs_dir.glob("*.wav"):
        if file.stat().st_mtime < cutoff_date.timestamp():
            archive_path = archive_dir / file.name
            file.rename(archive_path)
```

## Performance Considerations

### File System Optimization

**SSD vs HDD**:
- **Models directory**: SSD required for model loading performance
- **Reference audio**: SSD recommended for fast access
- **Outputs directory**: HDD acceptable, SSD preferred
- **Temp directory**: SSD recommended for processing speed

**Network Storage**:
- **Reference audio**: Network storage acceptable
- **Models**: Local storage required for performance
- **Outputs**: Network storage acceptable

### Monitoring and Maintenance

**Disk Usage Monitoring**:
```python
def check_disk_usage():
    total, used, free = shutil.disk_usage("/")
    usage_percent = (used / total) * 100
    
    if usage_percent > 90:
        cleanup_old_files()
        log_warning("Disk usage high")
```

**File Count Limits**:
- **outputs/**: Keep last 1000 files, archive older
- **temp/**: Auto-cleanup after 24 hours
- **logs/**: Rotate logs weekly

## See Also

- [Configuration Reference](configuration.md) - Path configuration
- [File Uploads Guide](../guides/file-uploads.md) - Upload file handling
- [Advanced Features Guide](../guides/advanced-features.md) - File management features
- [Audio Files Directory Structure](../../audio_files_directory_structure.md) - Detailed structure guide

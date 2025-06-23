# Audio Files Directory Structure

This document describes the directory structure and file organization for audio files in the Chatterbox TTS Extended Plus system.

## Directory Purpose Definition

```yaml
paths:
  reference_audio_dir: "reference_audio"  # ALL reference voices (TTS + VC targets)
  vc_input_dir: "vc_inputs"              # Source audio files to be converted  
  output_dir: "outputs"                  # Generated audio files
  temp_dir: "temp"                       # Downloaded URLs, temporary processing
```

## Directory Usage Examples

### `reference_audio/` - All Reference Voices
```
reference_audio/
├── tts_voices/                    # TTS reference voices
│   ├── narrator_formal.wav
│   ├── speaker1_casual.wav
│   └── presenter_energetic.wav
├── vc_targets/                    # Voice conversion target voices
│   ├── celebrity_voice.wav
│   ├── custom_character.wav
│   └── professional_speaker.wav
└── shared/                        # Voices used for both TTS and VC
    ├── main_character.wav
    └── brand_voice.wav
```

### `vc_inputs/` - Source Audio to Convert
```
vc_inputs/
├── meeting_recordings/
│   ├── team_call_2024.wav
│   └── client_presentation.mp3
├── podcasts/
│   ├── episode_01.wav
│   └── interview_raw.wav
└── personal/
    ├── speech_practice.wav
    └── voicemail.mp3
```

### `outputs/` - Generated Results
```
outputs/
├── tts_output_20240617_001.wav
├── tts_output_20240617_001.mp3
├── vc_output_20240617_002.wav
└── vc_output_20240617_002.flac
```

### `temp/` - Temporary Files
```
temp/
├── download_12345.wav           # Downloaded from URL
├── processing_chunk_1.wav       # Temporary processing files
└── cleanup_queue/               # Files scheduled for deletion
```

## File Resolution Logic

### For TTS API Call
```python
# POST /api/v1/tts
{
  "text": "Hello world",
  "reference_audio_filename": "narrator_formal.wav"  # or "tts_voices/narrator_formal"
}

# Resolution: looks in reference_audio_dir
# reference_audio/narrator_formal.wav
# OR reference_audio/tts_voices/narrator_formal.wav
```

### For VC API Call
```python
# POST /api/v1/vc  
{
  "input_audio_source": "team_call_2024.wav",        # looks in vc_input_dir
  "target_voice_source": "celebrity_voice.wav"       # looks in reference_audio_dir
}

# Resolution:
# input: vc_inputs/team_call_2024.wav (or subdirs)
# target: reference_audio/celebrity_voice.wav (or subdirs)
```

### URL Handling
```python
# VC with URL input
{
  "input_audio_source": "https://example.com/audio.mp3",  # downloads to temp/
  "target_voice_source": "celebrity_voice.wav"           # local file
}

# TTS with URL reference
{
  "text": "Hello world",
  "reference_audio_filename": "https://example.com/voice.wav"  # downloads to temp/
}
```

## Benefits of This Approach

1. **Clear Mental Model**: Users know exactly where to put each type of file
2. **Flexible Organization**: Can organize subdirectories within each main directory
3. **Consistent Logic**: Same resolution logic works for both local files and URLs
4. **Future-Proof**: Easy to add new file types or sources later
5. **Error-Friendly**: Clear error messages when files aren't found in expected locations

This structure makes it intuitive for users while keeping the implementation clean and maintainable.

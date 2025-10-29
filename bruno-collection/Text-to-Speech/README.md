# Text-to-Speech Endpoint - Bruno Requests

This folder contains comprehensive Bruno request files for testing all variants and features of the Text-to-Speech (TTS) endpoint.

## Overview

The Text-to-Speech endpoint generates speech from text with advanced features including voice cloning, quality validation, speed control, and audio trimming.

**Endpoint**: `POST /api/v1/tts`

## Request Files in This Folder

### Core Request Variants

**1. TTS - Basic Stream Response.bru**
- **Response**: Binary audio file streamed directly
- **Use Case**: Quick TTS generation with default parameters
- **Best For**: Testing, simple applications, default voice

**2. TTS - Stream with Format Selection.bru**
- **Response**: Stream specific format from multiple generated
- **Features**: Voice cloning, format selection, custom parameters
- **Best For**: Multi-format generation with immediate playback

**3. TTS - URL Response with Metadata.bru**
- **Response**: JSON with file URLs and metadata
- **Use Case**: Workflows needing metadata and processing info
- **Best For**: Batch processing, async workflows, metadata tracking

### Advanced Feature Examples

**4. TTS - Speed Control Example.bru**
- **Feature**: Adjust playback speed (0.5-2.0x)
- **Library**: audiostretchy for high-quality speed adjustment
- **Best For**: Audiobooks, learning materials, time-constrained content

**5. TTS - Audio Trimming Example.bru**
- **Feature**: Automatic silence removal from start/end
- **Use Case**: Professional audio production, clean output
- **Best For**: Podcasts, audiobooks, presentations

**6. TTS - Project Organization Example.bru**
- **Feature**: Organize files in project folders
- **Structure**: outputs/{project}/filename.wav
- **Best For**: Multi-project workflows, organized content management

## Quick Start

### Prerequisites

1. **Server Running**: Start API server on port 7860
2. **Environment**: Use "Local" environment in Bruno
3. **Reference Audio** (optional): Files in `reference_audio/` directory

### Recommended First Test

Start with **"TTS - Basic Stream Response"**:

1. Open the request file
2. Review the text parameter
3. Click "Send"
4. Download and play the streamed result

## Request Structure

### JSON Request Body
```json
{
  "text": "Text to synthesize",
  "reference_audio_filename": "speaker_en/jamie_vc_to_david-2.wav",
  "export_formats": ["wav", "mp3"],
  "temperature": 0.75,
  "seed": 42,
  "exaggeration": 0.5
}
```

### Query Parameters
- `response_mode`: "stream" (default) or "url"
- `return_format`: "wav", "mp3", or "flac" (for stream mode with multiple formats)

## Parameters Explained

### Core Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `text` | string | required | 1-10,000 chars | Text to synthesize into speech |
| `reference_audio_filename` | string | null | - | Voice reference file from `reference_audio/` |
| `export_formats` | array | ["wav","mp3"] | - | Output formats: "wav", "mp3", "flac" |
| `project` | string | null | - | Project folder for organizing files in `outputs/` |
| `folder` | string | null | - | Alias for `project` parameter |

### Voice Generation Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `exaggeration` | float | 0.5 | 0.0-1.0 | Voice expressiveness and emotion intensity |
| `temperature` | float | 0.75 | 0.0-2.0 | Generation randomness (lower = more consistent) |
| `seed` | integer | 0 | 0+ | Random seed for reproducibility (0 = random) |
| `cfg_weight` | float | 1.0 | 0.0-3.0 | Classifier-free guidance weight |

### Speed Control Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `speed_factor` | float | 1.0 | 0.5-2.0 | Playback speed multiplier |
| `speed_factor_library` | string | "auto" | - | Processing library: "auto", "audiostretchy", "librosa", "torchaudio" |

**Library Selection Guide**:
- **auto**: Smart selection with audiostretchy preferred (recommended)
- **audiostretchy**: Best quality, TDHS algorithm, formant preservation
- **librosa**: Good baseline compatibility
- **torchaudio**: Basic fallback (affects pitch)

### Audio Trimming Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `trim` | boolean | false | - | Apply silence trimming to generated audio |
| `trim_threshold_ms` | integer | 200 | 50-1000 | Silence threshold in milliseconds |

### Advanced Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_candidates_per_chunk` | integer | 3 | Number of generation candidates per text chunk |
| `max_attempts_per_candidate` | integer | 3 | Maximum retry attempts for failed generations |
| `bypass_whisper_checking` | boolean | false | Skip Whisper quality validation (faster) |
| `whisper_model_name` | string | "medium" | Whisper model: "tiny", "base", "small", "medium", "large" |
| `use_faster_whisper` | boolean | true | Use faster-whisper backend for validation |
| `disable_watermark` | boolean | true | Disable audio watermarking |

### Text Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_batching` | boolean | false | Enable text chunking and batching |
| `smart_batch_short_sentences` | boolean | true | Intelligently group short sentences |
| `to_lowercase` | boolean | true | Convert text to lowercase |
| `normalize_spacing` | boolean | true | Normalize whitespace and spacing |
| `fix_dot_letters` | boolean | true | Fix letter.dot.sequences (e.g., "U.S.A.") |
| `remove_reference_numbers` | boolean | true | Remove reference patterns like [1], (2) |

### Parameter Optimization

**Exaggeration Settings**:
- **0.3-0.4**: Calm, neutral delivery
- **0.5**: Default, balanced expressiveness
- **0.6-0.7**: More expressive, emotional
- **0.8-1.0**: Very expressive, dramatic

**Temperature Settings**:
- **0.5-0.7**: Consistent, predictable output
- **0.75**: Default, good balance
- **0.8-1.0**: More variety, less predictable
- **1.0+**: High variety, experimental

**Speed Factor Settings**:
- **0.5**: Half speed (very slow, learning materials)
- **0.8**: 20% slower (easier comprehension)
- **1.0**: Normal speed
- **1.3-1.5**: 30-50% faster (time-saving, still natural)
- **2.0**: Double speed (maximum)

**Format Selection**:
- **WAV**: Lossless, best quality, largest files (~10MB/min)
- **MP3**: Good quality, smallest files (~1MB/min), widely compatible
- **FLAC**: Lossless compressed, excellent balance (~5MB/min)

## Response Types

### Stream Response (response_mode=stream)

**Headers**:
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="tts_2025-10-29_143022_456_temp0.75_seed42.wav"
X-Alternative-Formats: mp3:/outputs/tts_2025-10-29_143022_456_temp0.75_seed42.mp3
```

**Body**: Binary audio data

**Download**: Bruno automatically detects and offers to save the file

### URL Response (response_mode=url)

**JSON Body**:
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_2025-10-29_143022_456_temp0.75_seed42.wav",
      "url": "/outputs/tts_2025-10-29_143022_456_temp0.75_seed42.wav",
      "path": "E:/Repos/Chatterbox-TTS-Extended-Plus/outputs/tts_2025-10-29_143022_456_temp0.75_seed42.wav"
    },
    {
      "format": "mp3",
      "filename": "tts_2025-10-29_143022_456_temp0.75_seed42.mp3",
      "url": "/outputs/tts_2025-10-29_143022_456_temp0.75_seed42.mp3",
      "path": "E:/Repos/Chatterbox-TTS-Extended-Plus/outputs/tts_2025-10-29_143022_456_temp0.75_seed42.mp3"
    }
  ],
  "generation_seed_used": 42,
  "processing_time_seconds": 5.2,
  "message": "TTS generation completed successfully",
  "timestamp": "2025-10-29T14:30:22Z"
}
```

## Testing Workflow

### Recommended Testing Order

1. **Basic Stream** → Test basic functionality with defaults
2. **Stream Format** → Test format selection and voice cloning
3. **URL Response** → Test metadata and URL mode
4. **Speed Control** → Test speed adjustment features
5. **Audio Trimming** → Test silence removal
6. **Project Organization** → Test folder organization

### Validation Checklist

For each request:
- [ ] Request completes with HTTP 200
- [ ] Response contains expected data/headers
- [ ] Generated files are playable
- [ ] File sizes are reasonable
- [ ] Alternative formats accessible (stream mode)
- [ ] Processing time acceptable
- [ ] Metadata accurate (URL mode)
- [ ] Voice cloning works correctly (if used)
- [ ] Advanced features work as expected

## File Setup Guide

### Reference Audio Files (Optional)

For voice cloning, place reference audio files in the `reference_audio/` directory:

```
reference_audio/
├── speaker_en/
│   ├── DAVID-2.mp3
│   └── jamie_vc_to_david-2.wav
├── test_voices/
│   ├── linda_johnson_01.mp3
│   └── linda_johnson_02.mp3
└── custom/
    └── my_voice.wav
```

### Reference Audio Requirements

- **Duration**: 10-30 seconds of clear speech
- **Quality**: High quality, minimal background noise
- **Format**: WAV, MP3, or FLAC
- **Content**: Natural speaking voice, not singing or effects

### Generated Files

TTS output files are saved to the `outputs/` directory:

**Without Project Parameter**:
```
outputs/
├── tts_2025-10-29_143022_456_temp0.75_seed42.wav
├── tts_2025-10-29_143022_456_temp0.75_seed42.mp3
└── tts_2025-10-29_143100_789_speed1.5.wav
```

**With Project Parameter** (project="my_audiobook/chapter_01"):
```
outputs/
└── my_audiobook/
    └── chapter_01/
        ├── tts_2025-10-29_143022_456_temp0.75_seed42.wav
        └── tts_2025-10-29_143022_456_temp0.75_seed42.mp3
```

## Troubleshooting

### Common Issues

**Text Too Long Error**:
- Text exceeds 10,000 character limit
- Split text into smaller chunks
- Consider using batching for long texts

**Reference Audio Not Found**:
- Verify file exists in `reference_audio/` directory
- Check file path spelling and structure
- Use relative path from `reference_audio/` root

**Poor Quality Output**:
- Use higher quality reference audio (10-30s clear speech)
- Adjust temperature (lower = more consistent)
- Adjust exaggeration for desired expressiveness
- Ensure reference audio has minimal noise

**Processing Too Slow**:
- Set `bypass_whisper_checking: true` for faster processing
- Reduce number of formats in `export_formats`
- Consider shorter text input
- Lower `num_candidates_per_chunk` value

**First Request Timeout**:
- Models load on first request (30-60s)
- Make a simple health check first: GET /api/v1/health
- Subsequent requests will be much faster

**Speed Control Issues**:
- Ensure speed_factor is within 0.5-2.0 range
- Try different libraries if quality is poor
- audiostretchy provides best results for speech
- Extreme speeds (< 0.7 or > 1.5) may sound unnatural

### Monitoring

**Check Server Logs**:
```powershell
Get-Content logs/chatterbox_extended.log -Tail 20
```

**Look For**:
- Error messages with context
- Processing duration times
- Model loading status
- Quality validation results

## Performance Benchmarks

**Typical Processing Times** (default parameters):
- 1-2 sentences: 2-5 seconds
- 1 paragraph: 5-15 seconds (with quality validation)
- Long text (batched): 30-60 seconds
- With voice cloning: +20-50% processing time

**Factors Affecting Speed**:
- Text length and complexity
- Quality validation (Whisper checking)
- Number of export formats
- Number of generation candidates
- Reference audio processing
- Speed adjustment processing

**Processing Time Examples**:
- Basic TTS (1 sentence, no validation): 2-3 seconds
- Voice cloning (1 paragraph): 8-12 seconds
- Speed adjusted (1.3x, audiostretchy): 10-15 seconds
- Trimmed audio: +1-2 seconds
- Multiple formats (3): +2-5 seconds

## Related Documentation

### Quick Reference
- **[TTS Quick Reference](../quick-reference/text-to-speech.md)** - Parameter guide and use case summary

### API Documentation
- **[TTS Endpoint Docs](../../docs/api/endpoints/tts.md)** - Complete API reference
- **[Speed Control Guide](../../docs/api/guides/advanced-features.md#speed-control)** - Detailed speed adjustment
- **[Error Handling](../../docs/api/guides/error-handling.md)** - Error codes and solutions

### Testing
- **[TTS Test Client](../../tests/test_tts_client.py)** - Python test client with examples

## Tips for Success

1. **Start Simple**: Use Basic Stream with default parameters first
2. **Test Incrementally**: Add features one at a time
3. **Monitor Logs**: Watch server logs during processing
4. **Optimize Parameters**: Adjust temperature, exaggeration based on results
5. **Choose Right Mode**: Stream for immediate use, URL for workflows
6. **Plan Formats**: Generate only formats you need to save time
7. **Use Voice Cloning**: High-quality reference audio makes a big difference
8. **Consider Speed Control**: audiostretchy library for best quality
9. **Trim When Needed**: Professional output benefits from trimming
10. **Organize Projects**: Use project folders for better file management

## Advanced Use Cases

### Audiobook Production
```json
{
  "text": "Chapter one. It was a dark and stormy night...",
  "reference_audio_filename": "narrators/professional_voice.wav",
  "project": "my_audiobook/chapter_01",
  "export_formats": ["wav", "mp3"],
  "temperature": 0.7,
  "exaggeration": 0.6,
  "trim": true,
  "seed": 100
}
```

### Learning Materials (Slower Speed)
```json
{
  "text": "In this lesson, we will learn about...",
  "speed_factor": 0.85,
  "speed_factor_library": "audiostretchy",
  "export_formats": ["mp3"],
  "bypass_whisper_checking": true
}
```

### Time-Constrained Content (Faster Speed)
```json
{
  "text": "Welcome to our quick daily news update...",
  "speed_factor": 1.4,
  "speed_factor_library": "audiostretchy",
  "export_formats": ["mp3"],
  "temperature": 0.75
}
```

### Reproducible Content Generation
```json
{
  "text": "This will sound exactly the same every time.",
  "seed": 42,
  "temperature": 0.6,
  "reference_audio_filename": "brand_voice/company_voice.wav",
  "export_formats": ["wav", "mp3"]
}
```

---

*For general Bruno collection information, see [main README](../README.md)*  
*Last updated: October 29, 2025*

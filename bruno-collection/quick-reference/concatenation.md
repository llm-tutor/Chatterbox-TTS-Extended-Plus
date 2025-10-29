# Audio Concatenation - Quick Reference

> **Endpoints**: POST /api/v1/concat (basic), POST /api/v1/concat/mixed (advanced)  
> **Purpose**: Combine multiple audio files with professional features  
> **Full Documentation**: [Audio Concatenation README](../Audio%20Concatenation/README.md)

## Request Variants Summary

| # | Name | Input Method | Response Mode | Use Case |
|---|------|--------------|---------------|----------|
| 1 | Basic Stream | JSON (server files) | Stream binary | Simple file combination |
| 2 | Basic URL | JSON (server files) | JSON with URLs | Metadata requirements |
| 3 | Basic Trimming | JSON (server files) | JSON with trim details | Silence removal |
| 4 | Basic Crossfade | JSON (server files) | Stream binary | Smooth transitions |
| 5 | Mixed Stream | Multipart (mixed sources) | Stream binary | Upload integration |
| 6 | Mixed Format | Multipart (mixed sources) | Stream specific format | Multiple formats |
| 7 | Mixed URL | Multipart (mixed sources) | JSON with URLs | Complete workflow |

## Mode Selection

### When to Use Basic Mode (POST /api/v1/concat)
- All files already exist in outputs/ directory
- Simple concatenation needs
- No file uploads required
- Quick assembly tasks

### When to Use Mixed Mode (POST /api/v1/concat/mixed)
- Need to upload new files
- Mix server files + uploads + silence
- Complex segment ordering
- Dynamic user content integration

## Parameter Quick Reference

### Crossfade Duration (crossfade_ms)
- **0ms**: No crossfade (direct join)
- **100-200ms**: Quick transition for speech
- **300-500ms**: Standard professional crossfade
- **1000+ms**: Long fade for music/ambient

### Trimming Threshold (trim_threshold_ms)
- **50-100ms**: Aggressive (removes brief pauses)
- **200ms**: Balanced (default)
- **300-500ms**: Conservative
- **trim**: Must be true to enable

### Natural Pause Settings
- **pause_duration_ms=0**: No automatic pauses
- **pause_duration_ms=400-600**: Natural speech pauses
- **pause_duration_ms=800-1000**: Dramatic narration pauses
- **pause_variation_ms=200**: Adds randomness (default)

### Silence Notation (Manual Insertion)
- `"(1s)"` - 1 second silence
- `"(500ms)"` - 500 milliseconds silence
- `"(2.5s)"` - 2.5 seconds silence

### Export Formats
- **JSON**: ["wav", "mp3", "flac"]
- **WAV**: Lossless, ~10MB/min
- **MP3**: Compressed, ~1MB/min
- **FLAC**: Lossless compressed, ~5MB/min

## Endpoint Details

### Basic Mode
**URL**: POST /api/v1/concat

**Query Parameters**:
- response_mode=stream (default, returns binary)
- response_mode=url (returns JSON)
- return_format=mp3 (which format to stream)

**Body** (JSON):
```json
{
  "files": ["file1.wav", "file2.mp3"],
  "export_formats": ["wav"],
  "normalize_levels": true
}
```

### Mixed Mode
**URL**: POST /api/v1/concat/mixed

**Content-Type**: multipart/form-data

**Fields**:
- request_json (JSON string with segments array)
- uploaded_files (audio files, multiple allowed)

**Segment Types**:
```json
{"type": "server_file", "source": "intro.wav"}
{"type": "upload", "index": 0}
{"type": "silence", "source": "(1s)"}
```

## Common Use Cases

### Podcast Production
```json
{
  "files": ["intro.mp3", "content.mp3", "outro.mp3"],
  "crossfade_ms": 300,
  "normalize_levels": true,
  "project": "podcast/episode01"
}
```

### Video Narration (Precise Timing)
```json
{
  "files": [
    "(1s)",
    "scene1_narration.wav",
    "(2s)",
    "scene2_narration.wav",
    "(500ms)"
  ],
  "trim": true,
  "normalize_levels": true
}
```

### Audiobook Assembly
```json
{
  "files": ["chapter1.wav", "chapter2.wav", "chapter3.wav"],
  "pause_duration_ms": 800,
  "pause_variation_ms": 150,
  "trim": true
}
```

### Mixed User Content
```
segments: [
  {"type": "server_file", "source": "intro.mp3"},
  {"type": "upload", "index": 0},
  {"type": "silence", "source": "(500ms)"},
  {"type": "server_file", "source": "outro.mp3"}
]
uploaded_files: @file(./user_recording.wav)
```

## Performance Estimates

**Basic Concatenation (3 files, 45s total)**:
- Simple: 1-2 seconds
- With trimming: 2-3 seconds
- With crossfade: 2-3 seconds
- All features: 3-5 seconds

**Mixed Concatenation (3 files + 2 uploads)**:
- Upload + process: 3-6 seconds
- With trimming: 4-8 seconds
- Full featured: 5-10 seconds

## Example File Paths

### Server-side Files (Basic Mode)
- Simple: "intro.wav", "main.mp3"
- Subfolder: "concatenation_test/01-sarah-audio.mp3"
- Project: "podcast/episode01/segment1.wav"

### Upload Files (Mixed Mode)
- Relative: @file(./test-files/recording.wav)
- Absolute: @file(C:/Users/You/audio.mp3)

## Tips

1. **Start with Basic Stream** for simple tasks
2. **Use URL mode** to debug trimming and get metadata
3. **Enable normalization** for consistent levels
4. **Test crossfade values** to find right transition feel
5. **Use project parameter** for organized output
6. **Mixed mode** when uploads needed

---

*For detailed documentation, troubleshooting, and advanced examples, see the [main Audio Concatenation README](../Audio%20Concatenation/README.md)*

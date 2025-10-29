# Audio Concatenation Endpoint - Bruno Requests

This folder contains comprehensive Bruno request files for testing all variants of the Audio Concatenation endpoint.

## Overview

The Audio Concatenation endpoint combines multiple audio files into a single file with professional audio production features including crossfading, silence insertion, trimming, and normalization.

**Endpoints**: 
- `POST /api/v1/concat` - Basic concatenation with server files
- `POST /api/v1/concat/mixed` - Advanced concatenation with mixed sources (server files + uploads + silence)

## Request Files in This Folder

### Basic Concatenation (Server Files Only)

**1. Concat - Basic Stream Response.bru**
- **Input Method**: JSON body with file paths from outputs/ directory
- **Response**: Binary audio file streamed directly
- **Use Case**: Quick combination of server-side files
- **Best For**: Simple podcast assembly, joining segments

**2. Concat - Basic URL Response.bru**
- **Input Method**: JSON body with file paths from outputs/ directory
- **Response**: JSON with file URLs and metadata
- **Use Case**: Workflows needing file information
- **Best For**: Web apps, batch processing, metadata requirements

**3. Concat - Basic with Trimming.bru**
- **Input Method**: JSON body with trimming enabled
- **Response**: JSON with detailed trim information
- **Features**: Automatic silence removal from input files
- **Best For**: Cleaning up recordings, professional production

**4. Concat - Basic with Crossfade.bru**
- **Input Method**: JSON body with crossfade settings
- **Response**: Binary audio with smooth transitions
- **Features**: Professional crossfade between segments
- **Best For**: Podcast production, music mixing, seamless audio

### Mixed-Mode Concatenation (Server Files + Uploads + Silence)

**5. Concat - Mixed Stream Response.bru**
- **Input Method**: Multipart form with file uploads
- **Response**: Binary audio file streamed directly
- **Features**: Mix server files, uploads, and silence segments
- **Best For**: User content integration, dynamic assembly

**6. Concat - Mixed Stream Format Selection.bru**
- **Input Method**: Multipart form with multiple format generation
- **Response**: Stream specific format with alternatives in header
- **Features**: Generate WAV, MP3, FLAC; stream preferred format
- **Best For**: Multi-format requirements, platform flexibility

**7. Concat - Mixed URL Response.bru**
- **Input Method**: Multipart form with comprehensive settings
- **Response**: JSON with detailed metadata
- **Features**: Complete feature demonstration with uploads
- **Best For**: Professional workflows, detailed feedback needs

## Quick Start

### Prerequisites

1. **Server Running**: Start API server on port 7860
2. **Environment**: Use "Local" environment in Bruno
3. **Test Files Ready**: 
   - **Basic mode**: Files in `outputs/concatenation_test/`
   - **Mixed mode**: Files in `outputs/` + local upload files

### Recommended First Test

Start with **"Concat - Basic Stream Response"**:

1. Open the request file
2. Verify test files exist:
   - `outputs/concatenation_test/01-sarah-audio.mp3`
   - `outputs/concatenation_test/02-mark-audio.mp3`
   - `outputs/concatenation_test/03-sarah-audio.mp3`
3. Click "Send"
4. Download and play the concatenated result

## Request Structure

### Basic Concatenation (JSON)
```json
{
  "files": [
    "concatenation_test/01-sarah-audio.mp3",
    "concatenation_test/02-mark-audio.mp3",
    "concatenation_test/03-sarah-audio.mp3"
  ],
  "export_formats": ["wav", "mp3"],
  "normalize_levels": true,
  "crossfade_ms": 300,
  "trim": true,
  "trim_threshold_ms": 200
}
```

### Mixed Concatenation (Multipart Form)
```
request_json: {
  "segments": [
    {"type": "server_file", "source": "intro.wav"},
    {"type": "silence", "source": "(1s)"},
    {"type": "upload", "index": 0},
    {"type": "server_file", "source": "outro.wav"}
  ],
  "export_formats": ["wav", "mp3"],
  "normalize_levels": true
}
uploaded_files: @file(./test-files/recording.wav)
```

### Query Parameters
- `response_mode`: "stream" (default) or "url"
- `return_format`: "wav", "mp3", or "flac" (for stream mode with multiple formats)

## Parameters Explained

### Core Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `files` | array[string] | required | 1+ items | List of filenames in outputs/ (basic mode) |
| `segments` | array[object] | required | 1+ items | Segment objects (mixed mode) |
| `export_formats` | array[string] | ["wav"] | wav,mp3,flac | Output audio formats |
| `normalize_levels` | boolean | true | - | Normalize audio levels across files |
| `crossfade_ms` | integer | 0 | 0-5000 | Crossfade duration in milliseconds |
| `pause_duration_ms` | integer | 0 | 0-3000 | Base pause between clips (natural mode) |
| `pause_variation_ms` | integer | 200 | 0-500 | Random variation in pause duration |
| `trim` | boolean | false | - | Remove silence from input files |
| `trim_threshold_ms` | integer | 200 | 50-1000 | Minimum silence duration to trim |
| `output_filename` | string | null | - | Custom filename (without extension) |
| `project` | string | null | - | Project folder path (e.g., "podcast/ep01") |

### Segment Object Structure (Mixed Mode)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | "server_file", "upload", or "silence" |
| `source` | string | conditional | Filename (server_file) or notation (silence) |
| `index` | integer | conditional | Upload file index (0-based) |

### Silence Notation

Manual silence segments use duration notation:
- `"(1s)"` - 1 second of silence
- `"(500ms)"` - 500 milliseconds of silence  
- `"(2.5s)"` - 2.5 seconds of silence


### Parameter Optimization

**Crossfade Duration** (crossfade_ms):
- **0ms**: Direct join, no crossfade
- **100-200ms**: Quick, subtle transition for speech
- **300-500ms**: Standard professional crossfade
- **500-1000ms**: Longer, dramatic transition for music
- **1000+ms**: Very long fade for ambient/atmospheric audio

**Trimming Threshold** (trim_threshold_ms):
- **50-100ms**: Aggressive trimming, removes brief pauses
- **200ms**: Default, balanced approach for most content
- **300-500ms**: Conservative, only removes significant silence
- **500+ms**: Very conservative, minimal trimming

**Natural Pause Settings**:
- **pause_duration_ms=0**: No automatic pauses (use manual silence only)
- **pause_duration_ms=400-600**: Natural speech pauses
- **pause_duration_ms=800-1000**: Dramatic pauses for narration
- **pause_variation_ms**: Adds randomness (0-500ms) for natural feel

**Format Selection**:
- **WAV**: Lossless, best quality, largest files (~10MB/min)
- **MP3**: Good quality, smallest files (~1MB/min), widely compatible
- **FLAC**: Lossless compressed, excellent balance (~5MB/min)

## Advanced Features

### Mixed-Mode Operation

The system intelligently handles mixed timing:

```json
{
  "files": [
    "intro.wav",           // File 1
    "(1s)",                // Manual 1000ms silence
    "main.wav",            // File 2
    "conclusion.wav",      // File 3 (no manual silence)
    "(500ms)",             // Manual 500ms silence
    "outro.wav"            // File 4
  ],
  "pause_duration_ms": 600,
  "pause_variation_ms": 200
}
```

**Resulting gaps:**
- intro.wav → **1000ms manual silence** → main.wav
- main.wav → **~600±200ms natural pause** → conclusion.wav
- conclusion.wav → **500ms manual silence** → outro.wav

### Trimming System

**How it Works:**
1. Analyzes each audio file for silence regions
2. Removes silence longer than `trim_threshold_ms`
3. Leaves 50ms buffer to avoid cutting content
4. Reports detailed trim information in response

**URL Response Shows Trim Details:**
```json
{
  "trim_info": {
    "trimmed": true,
    "original_duration_ms": 8500,
    "trimmed_duration_ms": 8150,
    "leading_silence_removed_ms": 250,
    "trailing_silence_removed_ms": 100
  }
}
```

### File Organization

**Project/Folder Parameter:**
```json
{
  "files": ["chapter1.wav", "chapter2.wav"],
  "output_filename": "full_book",
  "project": "audiobook/book1"
}
```

**Result:** Saved to `outputs/audiobook/book1/full_book.{wav,mp3}`

## Response Types

### Stream Mode (Default)
Returns audio file directly:

```http
Content-Type: audio/wav
Content-Disposition: attachment; filename="concat_2025-10-29_123456_789_3files_fade300_leveled.wav"
X-Alternative-Formats: mp3:/outputs/concat_2025-10-29_123456_789_3files_fade300_leveled.mp3
```

### URL Mode
Returns JSON with metadata:

```json
{
  "output_files": ["concat_2025-10-29_123456_789_3files_leveled.wav"],
  "generation_info": {
    "total_duration_seconds": 45.2,
    "file_count": 3,
    "silence_segments": 1,
    "processing_time_seconds": 1.8,
    "trim_applied": true,
    "files_trimmed": 2,
    "total_silence_removed_seconds": 0.85,
    "processing_details": [
      {
        "type": "file",
        "filename": "01-sarah-audio.mp3",
        "duration_seconds": 15.0,
        "trim_info": {
          "trimmed": true,
          "leading_silence_removed_ms": 150,
          "trailing_silence_removed_ms": 100
        }
      },
      {
        "type": "silence",
        "duration_ms": 1000,
        "source": "(1s)"
      }
    ]
  }
}
```

## Enhanced Filename Generation

Output filenames include processing parameters:

- **Basic**: `concat_2025-10-29_123456_789_3files_leveled.wav`
- **With Crossfade**: `concat_2025-10-29_123456_789_3files_fade300_leveled.wav`
- **With Silence**: `concat_2025-10-29_123456_789_3files_sil2_leveled.wav`
- **With Trimming**: `concat_2025-10-29_123456_789_3files_leveled_trim200.wav`
- **With Natural Pauses**: `concat_2025-10-29_123456_789_3files_pause600v200_leveled.wav`

## File Setup Guide

### Basic Mode Files

**1. Ensure Test Files Exist:**
```
outputs/concatenation_test/
├── 01-sarah-audio.mp3
├── 02-mark-audio.mp3
├── 03-sarah-audio.mp3
├── 01-sarah-audio-long.mp3      # For trimming tests
├── 02-mark-audio-long.mp3
└── 03-sarah-audio-long.mp3
```

**Future Improvement:**
Consider copying these test files to `bruno-collection/test-files/` to keep all Bruno testing resources within the collection folder.

**2. Update Request Paths:**
- Edit JSON bodies to match your actual file names
- Paths are relative to outputs/ directory
- Use forward slashes for subfolder paths

### Mixed Mode Files

**Option 1: Create test-files Directory** (Recommended)
```bash
mkdir bruno-collection/test-files
# Copy your audio files here
```

In Bruno requests:
```
uploaded_files: @file(./test-files/recording.wav)
```

**Option 2: Use Absolute Paths**
```
uploaded_files: @file(C:/Users/YourName/Music/recording.wav)
```


## Testing Workflow

### Recommended Testing Order

1. **Basic Stream** → Simple concatenation
2. **Basic with Trimming** → Silence removal features
3. **Basic with Crossfade** → Smooth transitions
4. **Basic URL** → Metadata and URL handling
5. **Mixed Stream** → File upload + mixed sources
6. **Mixed Stream Format** → Multiple format generation
7. **Mixed URL** → Complete advanced workflow

### Validation Checklist

For each request:
- [ ] Request completes with HTTP 200
- [ ] Response contains expected data/headers
- [ ] Generated files are playable
- [ ] File sizes are reasonable
- [ ] Alternative formats accessible (stream mode)
- [ ] Processing time acceptable
- [ ] Metadata accurate (URL mode)
- [ ] Trimming works as expected (if enabled)
- [ ] Crossfades sound smooth (if enabled)

## Use Cases and Examples

### Podcast Production
**Scenario**: Combine intro music, recorded content, and outro

**Basic Mode:**
```json
{
  "files": ["intro_music.mp3", "episode_content.mp3", "outro_music.mp3"],
  "crossfade_ms": 300,
  "normalize_levels": true,
  "trim": true,
  "project": "podcast/season01/episode03"
}
```

**Mixed Mode:**
```
segments: [
  {"type": "server_file", "source": "intro_music.mp3"},
  {"type": "silence", "source": "(500ms)"},
  {"type": "upload", "index": 0},
  {"type": "silence", "source": "(500ms)"},
  {"type": "server_file", "source": "outro_music.mp3"}
]
uploaded_files: @file(./recorded_episode.wav)
```

### Video Production
**Scenario**: Precise timing for video sync

```json
{
  "files": [
    "(1s)",
    "narration_intro.wav",
    "(2s)",
    "narration_main.wav",
    "(1.5s)",
    "narration_conclusion.wav",
    "(500ms)"
  ],
  "trim": true,
  "trim_threshold_ms": 150,
  "normalize_levels": true
}
```

### Audiobook Production
**Scenario**: Chapter assembly with natural flow

```json
{
  "files": ["chapter1.wav", "chapter2.wav", "chapter3.wav"],
  "pause_duration_ms": 800,
  "pause_variation_ms": 150,
  "trim": true,
  "output_filename": "full_book",
  "project": "audiobooks/scifi_novel"
}
```

### Music Mixing
**Scenario**: Smooth song transitions

```json
{
  "files": ["song1.mp3", "song2.mp3", "song3.mp3"],
  "crossfade_ms": 1000,
  "normalize_levels": true,
  "export_formats": ["wav", "mp3", "flac"]
}
```

## Troubleshooting

### Common Issues

**"File not found" Error**:
- **Basic mode**: Verify files exist in `outputs/` directory
- **Mixed mode**: Check server file paths and upload file paths
- Use forward slashes for subfolder paths
- Ensure no leading slash in file paths

**Upload Fails (Mixed Mode)**:
- Check file size limits
- Verify format: WAV, MP3, FLAC, OGG, M4A supported
- Ensure file is not corrupted
- Match upload index in segments array

**Poor Audio Quality**:
- Enable normalization: `"normalize_levels": true`
- Check input file quality
- Adjust crossfade duration for smoother transitions
- Use higher quality export formats (WAV or FLAC)

**Trimming Cuts Too Much**:
- Increase `trim_threshold_ms` (try 300-500ms)
- Use URL mode to inspect trim details
- Verify input files have actual silence to trim

**Processing Too Slow**:
- Reduce number of export formats
- Disable trimming if not needed
- Check server resources
- For large files, consider processing in parts

**First Request Timeout**:
- Models load on first request (may take time)
- Make a health check first: GET /api/v1/health
- Subsequent requests will be faster

**Crossfade Not Smooth**:
- Increase crossfade_ms (try 500-1000ms)
- Ensure input files have sufficient overlap potential
- Check audio levels are normalized
- Verify files are compatible (same sample rate helps)

### Segment Index Mismatch (Mixed Mode)

**Error**: "Expected 2 uploaded files, got 1"

**Solution**: Ensure upload count matches segment references:
```json
{
  "segments": [
    {"type": "upload", "index": 0},  // First upload
    {"type": "upload", "index": 1}   // Second upload
  ]
}
// Must have 2 uploaded_files fields
```

### Monitoring

**Check Server Logs:**
```powershell
Get-Content logs/chatterbox_extended.log -Tail 20
```

**Look For:**
- Processing duration times
- Trim operation results
- File processing stages
- Error messages with context

## Performance Benchmarks

**Typical Processing Times:**

**Basic Concatenation (3 files, ~45 seconds total):**
- Without trimming: 1-2 seconds
- With trimming: 2-3 seconds
- With crossfade: 2-3 seconds
- All features: 3-5 seconds

**Mixed Concatenation (3 files + 2 uploads):**
- Upload + processing: 3-6 seconds
- With trimming: 4-8 seconds
- Full featured: 5-10 seconds

**Factors Affecting Speed:**
- Total audio duration
- Number of files/segments
- Trimming enabled (adds analysis time)
- Number of export formats
- Upload file sizes
- System resources

## Related Documentation

### Quick Reference
- **[Concat Quick Reference](../quick-reference/concatenation.md)** - Parameter guide and use case summary

### API Documentation
- **[Concatenation Endpoint Docs](../../docs/api/endpoints/concatenation.md)** - Complete API reference
- **[File Uploads Guide](../../docs/api/guides/file-uploads.md)** - Upload specifications
- **[File Operations](../../docs/api/endpoints/file-operations.md)** - Output management
- **[Error Handling](../../docs/api/guides/error-handling.md)** - Error codes and solutions

### Testing
- **[Basic Concat Tests](../../tests/test_phase11_task_11_13_basic_concat_revision.py)** - Test suite for basic mode
- **[Mixed Concat Tests](../../tests/test_phase11_task_11_15_mixed_concat_revision.py)** - Test suite for mixed mode

## Tips for Success

1. **Start Simple**: Use Basic Stream with default parameters first
2. **Test Incrementally**: Add features one at a time
3. **Monitor Logs**: Watch server logs during processing
4. **Use URL Mode for Debugging**: Get detailed metadata about processing
5. **Optimize Parameters**: Adjust based on content type and quality needs
6. **Plan File Organization**: Use project parameter for clean folder structure
7. **Choose Right Mode**: Basic for server files, Mixed for uploads
8. **Test Trimming First**: Use URL mode to see what gets trimmed before committing

## Future Improvements

- **Test Files in Collection**: Copy test files from `outputs/concatenation_test/` to `bruno-collection/test-files/` for self-contained testing
- **Additional Examples**: More use-case specific examples (e.g., conference call assembly, music album creation)
- **Performance Profiles**: Pre-configured parameter sets for different quality/speed tradeoffs

---

*For general Bruno collection information, see [main README](../README.md)*  
*Last updated: October 29, 2025*

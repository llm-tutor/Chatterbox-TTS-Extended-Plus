# Audio Concatenation API

The concatenation API combines multiple audio files from the outputs directory into a single file with professional audio production features.

## Endpoint

```
POST /api/v1/concat
```

## Request Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `files` | array[string] | **required** | 1+ items | List of filenames and silence notations |
| `export_formats` | array[string] | `["wav"]` | wav, mp3, flac | Output audio formats |
| `normalize_levels` | boolean | `true` | - | Normalize audio levels across files |
| `crossfade_ms` | integer | `0` | 0-5000 | Crossfade duration in milliseconds |
| `pause_duration_ms` | integer | `0` | 0-3000 | Base pause duration between clips (0 = no pause, ignored when using manual silence) |
| `pause_variation_ms` | integer | `200` | 0-500 | Random variation in pause duration (+/-) |
| `trim` | boolean | `false` | - | Remove extraneous silence from input files before concatenation |
| `trim_threshold_ms` | integer | `200` | 50-1000 | Minimum silence duration to consider for trimming |
| `output_filename` | string | null | - | Custom output filename (without extension) |
| `response_mode` | string | `"stream"` | stream, url | Response format |

## Files Array Formats

### Basic File List
```json
{
  "files": [
    "intro.wav",
    "main_content.wav", 
    "outro.wav"
  ]
}
```

### With Manual Silence Insertion
```json
{
  "files": [
    "(1s)",              // 1 second of silence
    "intro.wav",
    "(500ms)",           // 500 milliseconds pause
    "main_content.wav",
    "(2.5s)",            // 2.5 second dramatic pause
    "outro.wav",
    "(1s)"               // Ending silence
  ]
}
```

## Audio Trimming System

The trimming system automatically detects and removes extraneous silence from the beginning and end of audio files before concatenation.

### How Trimming Works

1. **Silence Detection**: Uses librosa to analyze audio files for silence regions
2. **Threshold Filtering**: Only removes silence longer than `trim_threshold_ms`
3. **Conservative Approach**: Leaves a small buffer (50ms) to avoid cutting into audio content
4. **Smart Processing**: Skips files that don't have significant silence

### Trimming Parameters

- **`trim`**: Enable/disable trimming (default: false)
- **`trim_threshold_ms`**: Minimum silence duration to consider for removal (default: 200ms)
  - Range: 50-1000ms
  - Lower values = more aggressive trimming
  - Higher values = more conservative trimming

### Use Cases for Trimming

- **Video Production**: Clean up narration files with recording artifacts
- **Podcast Editing**: Remove inconsistent silence between segments
- **Audio Book Production**: Standardize chapter beginnings/endings
- **Professional Audio**: Ensure consistent timing across multiple takes

## Mixed-Mode Concatenation

The concatenation system supports **mixed-mode** operation where manual silences and natural pauses can coexist in a single request. This provides maximum flexibility for professional audio production.

### How Mixed-Mode Works

The system analyzes each gap between consecutive audio files and determines the appropriate behavior:

1. **Manual Silence**: When explicit silence notation `"(duration)"` is present
2. **Natural Pause**: When no manual silence is specified and `pause_duration_ms > 0`
3. **Direct Join**: When no manual silence is specified and `pause_duration_ms = 0`

### Parameter Interaction Logic

| Gap Type | Manual Silence Present | Pause Parameters | Result |
|----------|----------------------|------------------|--------|
| **Explicit** | `"(1s)"` between files | Ignored | Manual 1000ms silence |
| **Natural** | No notation | `pause_duration_ms=600` | Natural ~600±variation pause |
| **Direct** | No notation | `pause_duration_ms=0` | Direct join (0ms gap) |

### Mixed-Mode Example

Consider this files array with mixed timing requirements:
```json
{
  "files": [
    "intro.wav",           // File 1
    "(1s)",                // Manual 1000ms silence
    "main.wav",            // File 2
    "conclusion.wav",      // File 3 (no manual silence after)
    "(500ms)",             // Manual 500ms silence
    "outro.wav",           // File 4
    "credits.wav"          // File 5 (no manual silence after)
  ],
  "pause_duration_ms": 600,
  "pause_variation_ms": 200
}
```

**Resulting gaps:**
- intro.wav → **1000ms manual silence** → main.wav
- main.wav → **~600±200ms natural pause** → conclusion.wav
- conclusion.wav → **500ms manual silence** → outro.wav  
- outro.wav → **~600±200ms natural pause** → credits.wav

This gives users precise control where needed while maintaining natural flow elsewhere.

### Use Cases for Mixed-Mode

**Video Production**: Precise timing for video sync points, natural flow elsewhere
```json
{
  "files": ["scene1.wav", "(2s)", "scene2.wav", "scene3.wav", "(1s)", "scene4.wav"],
  "pause_duration_ms": 400,
  "trim": true
}
```

**Podcast Production**: Structured segments with conversational flow
```json
{
  "files": ["intro.wav", "(500ms)", "segment1.wav", "segment2.wav", "segment3.wav", "(1s)", "outro.wav"],
  "pause_duration_ms": 800,
  "pause_variation_ms": 150,
  "crossfade_ms": 200
}
```

**Audiobook Production**: Chapter breaks with natural reading flow
```json
{
  "files": ["(1s)", "chapter1.wav", "(3s)", "chapter2.wav", "chapter3.wav", "(3s)", "chapter4.wav"],
  "pause_duration_ms": 600,
  "trim": true
}
```

## Response Modes

### Stream Mode (Default)
Returns audio file directly for immediate download:

```http
Content-Type: audio/wav
Content-Disposition: attachment; filename="concat_2025-06-25_123456_789012_2files_leveled_trim200.wav"
```

### URL Mode
Returns JSON with file information:

```json
{
  "output_files": ["concat_2025-06-25_123456_789012_3files_sil2_leveled_trim200.wav"],
  "generation_info": {
    "total_duration_seconds": 45.2,
    "file_count": 3,
    "silence_segments": 2,
    "natural_pauses": 1,
    "processing_time_seconds": 1.8,
    "trim_applied": true,
    "files_trimmed": 2,
    "files_not_trimmed": 1,
    "total_silence_removed_seconds": 0.85,
    "processing_details": [
      {
        "type": "file",
        "filename": "intro.wav",
        "duration_seconds": 8.15,
        "trim_info": {
          "trimmed": true,
          "original_duration_ms": 8500,
          "trimmed_duration_ms": 8150,
          "leading_silence_removed_ms": 250,
          "trailing_silence_removed_ms": 100
        }
      },
      {
        "type": "manual_silence",
        "duration_ms": 1000,
        "duration_seconds": 1.0,
        "notation": "(1s)"
      },
      {
        "type": "file", 
        "filename": "main.wav",
        "duration_seconds": 25.5,
        "trim_info": {
          "trimmed": false,
          "original_duration_ms": 25500,
          "trimmed_duration_ms": 25500,
          "leading_silence_removed_ms": 0,
          "trailing_silence_removed_ms": 0
        }
      },
      {
        "type": "natural_pause",
        "duration_ms": 724,
        "duration_seconds": 0.724,
        "base_duration_ms": 600,
        "variation_applied_ms": 124
      },
      {
        "type": "file",
        "filename": "outro.wav", 
        "duration_seconds": 9.8,
        "trim_info": {
          "trimmed": true,
          "original_duration_ms": 10150,
          "trimmed_duration_ms": 9800,
          "leading_silence_removed_ms": 150,
          "trailing_silence_removed_ms": 200
        }
      }
    ]
  }
}
```

## Enhanced Filename Generation

Output files include processing parameters in the filename:

- **Basic**: `concat_2025-06-25_123456_789012_2files_leveled.wav`
- **With Natural Pauses**: `concat_2025-06-25_123456_789012_2files_pause600v200_leveled.wav`
- **With Manual Silence**: `concat_2025-06-25_123456_789012_2files_sil3_leveled.wav`
- **Mixed-Mode**: `concat_2025-06-25_123456_789012_3files_sil2_leveled_trim200.wav`
- **With Trimming**: `concat_2025-06-25_123456_789012_2files_leveled_trim200.wav`
- **With Crossfade**: `concat_2025-06-25_123456_789012_2files_fade500_leveled.wav`

## Examples

### Basic Concatenation
```bash
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["intro.wav", "main.wav", "outro.wav"],
    "export_formats": ["wav", "mp3"],
    "response_mode": "url"
  }'
```

### Professional Video Production
```bash
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
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
    "normalize_levels": true,
    "export_formats": ["wav"],
    "response_mode": "url"
  }'
```

### Podcast Production with Crossfade
```bash
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["segment1.wav", "segment2.wav", "segment3.wav"],
    "crossfade_ms": 300,
    "trim": true,
    "trim_threshold_ms": 200,
    "normalize_levels": true,
    "export_formats": ["mp3"],
    "response_mode": "stream"
  }'
```

### Natural Pause Concatenation
```bash
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["chapter1.wav", "chapter2.wav", "chapter3.wav"],
    "pause_duration_ms": 800,
    "pause_variation_ms": 150,
    "trim": true,
    "normalize_levels": true,
    "response_mode": "url"
  }'
```

### Mixed-Mode Concatenation
```bash
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "intro.wav",
      "(1s)",
      "main_segment.wav",
      "transition_segment.wav", 
      "(500ms)",
      "conclusion.wav",
      "final_segment.wav"
    ],
    "pause_duration_ms": 600,
    "pause_variation_ms": 200,
    "trim": true,
    "trim_threshold_ms": 150,
    "normalize_levels": true,
    "export_formats": ["wav"],
    "response_mode": "url"
  }'
```

*This example produces:*
- intro.wav → 1000ms manual silence → main_segment.wav
- main_segment.wav → ~600±200ms natural pause → transition_segment.wav  
- transition_segment.wav → 500ms manual silence → conclusion.wav
- conclusion.wav → ~600±200ms natural pause → final_segment.wav

## Error Responses

### File Not Found
```json
{
  "detail": "File not found: missing_file.wav"
}
```

### Invalid Audio Format
```json
{
  "detail": "Not an audio file: document.pdf"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "trim_threshold_ms"],
      "msg": "ensure this value is greater than or equal to 50"
    }
  ]
}
```

## Performance Notes

- **File Size**: Large files (>100MB) may take longer to process
- **Trimming Overhead**: Adds ~10-20% processing time for silence analysis
- **Memory Usage**: Scales with total audio duration and number of files
- **Temporary Files**: Trimming creates temporary files that are automatically cleaned up
- **Batch Processing**: Concatenating many files benefits from trimming to reduce total size

## Best Practices

1. **Use Trimming Selectively**: Enable only when files have known silence issues
2. **Test Thresholds**: Start with default 200ms threshold, adjust based on content
3. **Monitor Output Quality**: Verify trimming doesn't cut into actual content
4. **Combine Features**: Use trimming with normalization for best results
5. **File Organization**: Keep source files in outputs/ directory for easy access

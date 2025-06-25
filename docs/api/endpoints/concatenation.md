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
| `pause_duration_ms` | integer | `600` | 0-3000 | Base pause duration between clips (ignored with manual silence) |
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
  "output_files": ["concat_2025-06-25_123456_789012_2files_leveled_trim200.wav"],
  "generation_info": {
    "total_duration_seconds": 45.2,
    "file_count": 2,
    "processing_time_seconds": 1.8,
    "trim_applied": true,
    "files_trimmed": 1,
    "files_not_trimmed": 1,
    "total_silence_removed_seconds": 0.85,
    "trim_metadata": [
      {
        "original_file": "intro.wav",
        "trim_info": {
          "trimmed": true,
          "original_duration_ms": 8500,
          "trimmed_duration_ms": 8150,
          "leading_silence_removed_ms": 250,
          "trailing_silence_removed_ms": 100
        }
      }
    ]
  }
}
```

## Enhanced Filename Generation

Output files include processing parameters in the filename:

- **Basic**: `concat_2025-06-25_123456_789012_2files_leveled.wav`
- **With Pauses**: `concat_2025-06-25_123456_789012_2files_pause600v200_leveled.wav`
- **With Silence**: `concat_2025-06-25_123456_789012_2files_sil3_leveled.wav`
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

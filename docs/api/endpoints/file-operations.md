# File Operations Endpoints

List, download, and manage generated audio files and outputs.

## Overview

File operations endpoints provide:
- List all generated audio files with metadata
- Download individual files directly
- Search and filter generated content
- Pagination for large file collections

## List Generated Files

**GET** `/api/v1/outputs`

List generated audio files with metadata, pagination, and search capabilities.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number for pagination |
| `page_size` | integer | 50 | Number of files per page (max 100) |
| `generation_type` | string | - | Filter by type: `"tts"`, `"vc"`, `"concat"` |
| `search` | string | - | Search term for filenames or metadata |
| `sort_by` | string | `"created_date"` | Sort by: `"filename"`, `"created_date"`, `"file_size"`, `"generation_type"` |
| `sort_order` | string | `"desc"` | Sort order: `"asc"` or `"desc"` |
| `date_from` | string | - | Filter files created after date (ISO 8601) |
| `date_to` | string | - | Filter files created before date (ISO 8601) |
| `filenames` | string | - | Comma-separated list of specific filenames |

### Example Requests

#### Basic File List

```bash
curl "http://localhost:7860/api/v1/outputs?page=1&page_size=20"
```

#### Search and Filter

```bash
curl "http://localhost:7860/api/v1/outputs?generation_type=tts&search=speaker1&sort_by=created_date&sort_order=desc"
```

#### Date Range Filter

```bash
curl "http://localhost:7860/api/v1/outputs?date_from=2025-06-22T00:00:00Z&date_to=2025-06-22T23:59:59Z"
```

#### Specific Files Lookup

```bash
curl "http://localhost:7860/api/v1/outputs?filenames=tts_output_123.wav,vc_output_456.wav"
```

### Response

```json
{
  "success": true,
  "files": [
    {
      "filename": "tts_2025-06-22_143022_456_temp0.75_seed42.wav",
      "generation_type": "tts",
      "file_size_bytes": 276480,
      "created_date": "2025-06-22T14:30:22Z",
      "url": "/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.wav",
      "formats": [
        {
          "format": "wav",
          "filename": "tts_2025-06-22_143022_456_temp0.75_seed42.wav",
          "url": "/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.wav",
          "file_size_bytes": 276480
        },
        {
          "format": "mp3",
          "filename": "tts_2025-06-22_143022_456_temp0.75_seed42.mp3",
          "url": "/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.mp3",
          "file_size_bytes": 138240
        }
      ],
      "metadata": {
        "processing_time_seconds": 5.2,
        "parameters": {
          "text": "Original input text",
          "temperature": 0.75,
          "seed": 42
        }
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 20,
    "total_files": 125,
    "total_pages": 7,
    "has_next": true,
    "has_previous": false
  },
  "summary": {
    "total_files": 125,
    "total_size_bytes": 52428800,
    "generation_types": {
      "tts": 75,
      "vc": 45,
      "concat": 5
    }
  },
  "timestamp": "2025-06-22T14:30:22Z"
}
```

### Response Fields

#### File Object

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Primary filename (usually WAV) |
| `generation_type` | string | Type: `"tts"`, `"vc"`, `"concat"` |
| `file_size_bytes` | integer | Size of primary file in bytes |
| `created_date` | string | ISO 8601 creation timestamp |
| `url` | string | Direct download URL |
| `formats` | array | All available formats for this generation |
| `metadata` | object | Generation parameters and statistics |

#### Format Object

| Field | Type | Description |
|-------|------|-------------|
| `format` | string | Audio format (wav, mp3, flac) |
| `filename` | string | Format-specific filename |
| `url` | string | Direct download URL for this format |
| `file_size_bytes` | integer | File size in bytes |

## Download Generated Files

**GET** `/outputs/{filename}`

Download individual generated audio files directly.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Name of the file to download |

### Example Requests

#### Direct File Download

```bash
curl -O http://localhost:7860/outputs/tts_2025-06-22_143022_456.wav
```

#### Download with Custom Name

```bash
curl http://localhost:7860/outputs/vc_output_789.wav -o my_converted_voice.wav
```

### Response

Returns the audio file directly with appropriate headers:

```
HTTP/1.1 200 OK
Content-Type: audio/wav
Content-Length: 276480
Content-Disposition: attachment; filename="tts_2025-06-22_143022_456.wav"
Cache-Control: public, max-age=3600

[Binary audio data]
```

### Content Types by Format

| Format | Content-Type |
|--------|--------------|
| WAV | `audio/wav` |
| MP3 | `audio/mpeg` |
| FLAC | `audio/flac` |

## Python Examples

### List Generated Files

```python
import requests
from datetime import datetime, timedelta

def list_generated_files(generation_type=None, search=None, page=1, page_size=20):
    params = {
        'page': page,
        'page_size': page_size,
        'sort_by': 'created_date',
        'sort_order': 'desc'
    }
    
    if generation_type:
        params['generation_type'] = generation_type
    if search:
        params['search'] = search
    
    response = requests.get(
        "http://localhost:7860/api/v1/outputs",
        params=params
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['pagination']['total_files']} files:")
        for file_info in result['files']:
            print(f"  {file_info['filename']} ({file_info['generation_type']})")
            print(f"    Created: {file_info['created_date']}")
            print(f"    Size: {file_info['file_size_bytes']} bytes")
        return result
    else:
        print(f"Failed to list files: {response.status_code}")

# Usage examples
list_generated_files()  # List all files
list_generated_files(generation_type="tts")  # TTS files only
list_generated_files(search="speaker1")  # Search for specific content
```

### Download Files

```python
import requests
import os

def download_file(filename, local_path=None):
    if not local_path:
        local_path = filename
    
    response = requests.get(
        f"http://localhost:7860/outputs/{filename}",
        stream=True
    )
    
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {local_path}")
        return local_path
    else:
        print(f"Download failed: {response.status_code}")

def download_latest_tts():
    # Get latest TTS file
    files = list_generated_files(generation_type="tts", page_size=1)
    if files and files['files']:
        latest_file = files['files'][0]
        filename = latest_file['filename']
        download_file(filename)
        return filename
    else:
        print("No TTS files found")

# Usage
download_file("tts_output_123.wav")
download_latest_tts()
```

### Search Files by Date Range

```python
from datetime import datetime, timedelta

def get_recent_files(hours=24):
    now = datetime.utcnow()
    since = now - timedelta(hours=hours)
    
    params = {
        'date_from': since.isoformat() + 'Z',
        'sort_by': 'created_date',
        'sort_order': 'desc'
    }
    
    response = requests.get(
        "http://localhost:7860/api/v1/outputs",
        params=params
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Files created in last {hours} hours: {len(result['files'])}")
        return result['files']
    else:
        print(f"Search failed: {response.status_code}")

# Get files from last 6 hours
recent_files = get_recent_files(6)
```

### Concatenate Audio Files

```python
import requests

def concatenate_audio(files, pause_ms=600, variation_ms=200, crossfade_ms=0, 
                     formats=None, normalize=True):
    """
    Concatenate multiple audio files with natural pauses
    
    Args:
        files: List of filenames from outputs directory
        pause_ms: Base pause duration between clips (0-3000ms)
        variation_ms: Random variation in pause duration (0-500ms)
        crossfade_ms: Crossfade duration in milliseconds (0-5000ms)
        formats: List of output formats ['wav', 'mp3', 'flac']
        normalize: Whether to normalize audio levels
    
    Returns:
        Response object with concatenation results
    """
    if formats is None:
        formats = ['wav']
        
    payload = {
        "files": files,
        "export_formats": formats,
        "normalize_levels": normalize,
        "crossfade_ms": crossfade_ms,
        "pause_duration_ms": pause_ms,
        "pause_variation_ms": variation_ms,
        "response_mode": "url"  # Get metadata instead of streaming
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/concat",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example: Basic concatenation with natural pauses
files_to_concat = [
    "tts_2025-06-22_143022_456_temp0.75_seed42.wav",
    "tts_2025-06-22_143045_789_temp0.8_seed123.wav"
]

result = concatenate_audio(files_to_concat)
print(f"Created: {result['output_files'][0]}")
print(f"Duration: {result['total_duration_seconds']}s")
print(f"Pause added: {result['metadata']['total_pause_duration_ms']}ms")

# Example: Custom timing for dramatic effect
dramatic_result = concatenate_audio(
    files_to_concat,
    pause_ms=1500,      # 1.5 second pauses
    variation_ms=300,   # ±300ms variation
    formats=['wav', 'mp3']
)

# Example: Fast speech with minimal pauses
news_style = concatenate_audio(
    files_to_concat,
    pause_ms=300,       # Short pauses
    variation_ms=50,    # Minimal variation
    crossfade_ms=200    # Slight overlap
)

# Example: No pauses (legacy behavior)
no_pause_result = concatenate_audio(
    files_to_concat,
    pause_ms=0,         # Disable pauses
    crossfade_ms=500    # Use crossfade only
)
```

### Download Concatenated Files

```python
def download_concatenated_audio(files, output_path, **concat_options):
    """
    Concatenate audio and download directly to file
    
    Args:
        files: List of filenames to concatenate
        output_path: Local path to save the concatenated audio
        **concat_options: Additional concatenation parameters
    """
    # Set to streaming mode for direct download
    payload = {
        "files": files,
        "response_mode": "stream",
        **concat_options
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/concat",
        json=payload,
        stream=True,
        timeout=60
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded concatenated audio to: {output_path}")
    else:
        response.raise_for_status()

# Example: Direct download
download_concatenated_audio(
    files=["segment1.wav", "segment2.wav", "segment3.wav"],
    output_path="combined_speech.wav",
    pause_duration_ms=800,
    export_formats=["wav"]
)
```

## JavaScript Examples

### Fetch and Display Files

```javascript
async function listFiles(options = {}) {
    const params = new URLSearchParams({
        page: options.page || 1,
        page_size: options.pageSize || 20,
        sort_by: options.sortBy || 'created_date',
        sort_order: options.sortOrder || 'desc'
    });
    
    if (options.generationType) {
        params.append('generation_type', options.generationType);
    }
    if (options.search) {
        params.append('search', options.search);
    }
    
    try {
        const response = await fetch(
            `http://localhost:7860/api/v1/outputs?${params}`
        );
        const data = await response.json();
        
        console.log(`Found ${data.pagination.total_files} files`);
        data.files.forEach(file => {
            console.log(`${file.filename} (${file.generation_type})`);
        });
        
        return data;
    } catch (error) {
        console.error('Failed to fetch files:', error);
    }
}

// Usage
listFiles({ generationType: 'tts', pageSize: 10 });
```

### Download Files in Browser

```javascript
async function downloadFile(filename, customName = null) {
    try {
        const response = await fetch(`http://localhost:7860/outputs/${filename}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            // Create download link
            const a = document.createElement('a');
            a.href = url;
            a.download = customName || filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // Clean up
            URL.revokeObjectURL(url);
            console.log(`Downloaded: ${filename}`);
        } else {
            console.error(`Download failed: ${response.status}`);
        }
    } catch (error) {
        console.error('Download error:', error);
    }
}

// Usage
downloadFile('tts_output_123.wav');
downloadFile('voice_conversion_456.wav', 'my_converted_voice.wav');
```

## Concatenate Audio Files

**POST** `/api/v1/concat`

Combine multiple generated audio files into a single file with natural pauses and optional crossfading.

### Request Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `files` | array[string] | - | Yes | List of filenames from outputs directory (minimum 2) |
| `export_formats` | array[string] | `["wav"]` | No | Output formats: `"wav"`, `"mp3"`, `"flac"` |
| `normalize_levels` | boolean | `true` | No | Normalize audio levels to prevent clipping |
| `crossfade_ms` | integer | `0` | No | Crossfade duration in milliseconds (0-5000) |
| `pause_duration_ms` | integer | `600` | No | Base pause duration between clips (0-3000ms) |
| `pause_variation_ms` | integer | `200` | No | Random variation in pause duration (0-500ms) |
| `output_filename` | string | - | No | Custom output filename (without extension) |
| `response_mode` | string | `"stream"` | No | Response mode: `"stream"` or `"url"` |

### Natural Pause System

The concatenation endpoint includes a research-based natural pause system that addresses the common issue of audio clips sounding "tacked on" or rushed when joined together:

- **Default Pauses**: 600ms ± 200ms variation (based on speech research for optimal naturalness)
- **Customizable Duration**: Adjust `pause_duration_ms` for different styles:
  - 400ms: Faster speech/news reading
  - 600ms: Natural conversation (default)  
  - 1000ms+: Dramatic pauses/presentations
- **Random Variation**: Prevents mechanical, regular spacing between clips
- **Disable Option**: Set `pause_duration_ms: 0` for legacy behavior (no pauses)

### Crossfade Compatibility

Pauses and crossfading can be used together:
- **With pauses**: Crossfade first, then add pause for natural spacing
- **Without pauses**: Standard crossfade behavior (audio overlap)

### Example Requests

#### Basic Concatenation with Natural Pauses

```bash
curl -X POST "http://localhost:7860/api/v1/concat" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "tts_2025-06-22_143022_456_temp0.75_seed42.wav",
      "tts_2025-06-22_143045_789_temp0.8_seed123.wav"
    ]
  }'
```

#### Custom Pause Timing

```bash
curl -X POST "http://localhost:7860/api/v1/concat" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "tts_output_1.wav",
      "tts_output_2.wav", 
      "tts_output_3.wav"
    ],
    "pause_duration_ms": 1000,
    "pause_variation_ms": 300,
    "export_formats": ["wav", "mp3"]
  }'
```

#### Crossfade with Pauses

```bash
curl -X POST "http://localhost:7860/api/v1/concat" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["segment1.wav", "segment2.wav"],
    "crossfade_ms": 500,
    "pause_duration_ms": 800,
    "normalize_levels": true
  }'
```

#### No Pauses (Legacy Behavior)

```bash
curl -X POST "http://localhost:7860/api/v1/concat" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["audio1.wav", "audio2.wav"],
    "pause_duration_ms": 0,
    "response_mode": "url"
  }'
```

### Response

#### Streaming Response (Default)

When `response_mode="stream"` (default), returns the audio file directly for download:

```
Content-Type: audio/wav (or audio/mpeg, audio/flac)
Content-Disposition: attachment; filename="concat_2025-06-22_143100_123_2files_pause600±200_leveled.wav"

[Binary audio data]
```

#### URL Response

When `response_mode="url"`, returns metadata with file URLs:

```json
{
  "success": true,
  "message": "Audio concatenation completed successfully",
  "output_files": [
    "concat_2025-06-22_143100_123_2files_pause600±200_leveled.wav",
    "concat_2025-06-22_143100_123_2files_pause600±200_leveled.mp3"
  ],
  "total_duration_seconds": 8.45,
  "file_count": 2,
  "processing_time_seconds": 0.23,
  "metadata": {
    "total_duration_seconds": 8.45,
    "file_count": 2,
    "processing_time_seconds": 0.23,
    "processed_files": [
      {
        "filename": "tts_output_1.wav",
        "duration_seconds": 3.2,
        "size_bytes": 307200
      },
      {
        "filename": "tts_output_2.wav", 
        "duration_seconds": 4.1,
        "size_bytes": 393600
      }
    ],
    "output_size_bytes": 811200,
    "crossfade_ms": 500,
    "normalized": true,
    "pause_duration_ms": 600,
    "pause_variation_ms": 200,
    "total_pause_duration_ms": 643
  }
}
```

### Error Responses

#### Missing Files (404)
```json
{
  "detail": "File not found: non_existent_file.wav"
}
```

#### Invalid Parameters (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "files"],
      "msg": "At least 2 files required for concatenation"
    }
  ]
}
```

#### Unsupported Format (400)
```json
{
  "detail": "Not an audio file: document.txt"
}
```


## File Management

### Generated File Naming Convention

Files are automatically named with descriptive patterns:

#### TTS Files
```
tts_YYYY-MM-DD_HHMMSS_microseconds_temp{temperature}_seed{seed}.{format}
tts_2025-06-22_143022_456_temp0.75_seed42.wav
```

#### Voice Conversion Files
```
vc_YYYY-MM-DD_HHMMSS_microseconds_chunk{seconds}_overlap{seconds}_voice{target}.{format}
vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.wav
```

#### Concatenation Files
```
concat_YYYY-MM-DD_HHMMSS_microseconds_{count}files_[pause{duration}v{variation}]_[fade{ms}]_leveled.{format}

# Examples:
concat_2025-06-22_143100_123_2files_pause600v200_leveled.wav          # Natural pauses
concat_2025-06-22_143100_123_3files_pause1000_fade500_leveled.wav     # Custom pauses + crossfade  
concat_2025-06-22_143100_123_2files_fade300_leveled.wav               # Crossfade only
concat_2025-06-22_143100_123_2files_leveled.wav                       # No pauses, no crossfade
```

### File Organization

All generated files are stored in the `outputs/` directory:

```
outputs/
├── tts_2025-06-22_143022_456_temp0.75_seed42.wav
├── tts_2025-06-22_143022_456_temp0.75_seed42.mp3
├── vc_2025-06-22_143045_789_chunk60_overlap0.1.wav
├── vc_2025-06-22_143045_789_chunk60_overlap0.1.mp3
└── concat_2025-06-22_143100_123_3files.wav
```

### Storage Considerations

- **File retention**: No automatic cleanup (user managed)
- **Disk space**: Monitor output directory size
- **Formats**: Multiple formats increase storage usage
- **Metadata**: JSON companion files for detailed information

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "File not found",
  "detail": "The requested file does not exist in the outputs directory",
  "error_code": "FILE_NOT_FOUND",
  "timestamp": "2025-06-22T14:30:22Z"
}
```

### Error Types

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `FILE_NOT_FOUND` | 404 | Requested file doesn't exist | Check filename and availability |
| `VALIDATION_ERROR` | 400 | Invalid query parameters | Verify parameter formats |
| `PERMISSION_DENIED` | 403 | File access not allowed | Check file permissions |
| `SERVER_ERROR` | 500 | Internal file system error | Retry request or check logs |

## Performance Tips

### Efficient File Listing

1. **Use pagination**: Don't fetch all files at once for large collections
2. **Filter appropriately**: Use generation_type and date filters
3. **Limit page size**: Keep page_size reasonable (20-50 items)
4. **Cache results**: Store frequently accessed file lists

### Download Optimization

1. **Stream downloads**: Use streaming for large files
2. **Parallel downloads**: Download multiple files concurrently (with limits)
3. **Resume capability**: Handle interrupted downloads gracefully
4. **Format selection**: Choose appropriate format for your needs

## Related Endpoints

- **[TTS Endpoint](tts.md)** - Generate files that appear in listings
- **[Voice Conversion](voice-conversion.md)** - Create converted audio files
- **[Voice Management](voice-management.md)** - Manage reference voices

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*

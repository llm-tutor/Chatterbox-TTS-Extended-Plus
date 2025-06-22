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
concat_YYYY-MM-DD_HHMMSS_microseconds_{count}files_leveled.{format}
concat_2025-06-22_143100_123_3files_leveled.wav
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

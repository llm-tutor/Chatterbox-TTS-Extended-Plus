# Response Models

> **Chatterbox TTS Extended Plus** - Complete API response schemas and data structures

## Overview

This document describes all response models returned by the Chatterbox TTS API, including success responses, error responses, and metadata structures.

## Base Response Structure

### BaseResponse
```json
{
  "success": true,
  "message": "string (optional)"
}
```

All successful API responses inherit from this base structure.

### ErrorResponse
```json
{
  "success": false,
  "error": "Human-readable error message",
  "detail": "Technical details for debugging (optional)",
  "error_code": "MACHINE_READABLE_CODE", 
  "timestamp": "2025-06-22T14:30:00Z (optional)"
}
```

## Generation Response Models

### TTSResponse

**Stream Mode** (Default):
- **Content-Type**: `audio/wav` (or requested format)
- **Content-Disposition**: `attachment; filename="tts_timestamp.wav"`
- **X-Alternative-Formats**: `mp3:/outputs/file.mp3|flac:/outputs/file.flac`

**JSON Mode** (`response_mode=url`):
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_2025-06-22_143022_456.wav",
      "url": "/outputs/tts_2025-06-22_143022_456.wav",
      "path": "/full/path/to/file.wav"
    },
    {
      "format": "mp3", 
      "filename": "tts_2025-06-22_143022_456.mp3",
      "url": "/outputs/tts_2025-06-22_143022_456.mp3",
      "path": "/full/path/to/file.mp3"
    }
  ],
  "generation_seed_used": 42,
  "processing_time_seconds": 3.27
}
```

### VCResponse

**Stream Mode** (Default):
- **Content-Type**: `audio/wav` (or requested format)
- **Content-Disposition**: `attachment; filename="vc_timestamp.wav"`
- **X-Alternative-Formats**: `mp3:/outputs/file.mp3|flac:/outputs/file.flac`

**JSON Mode** (`response_mode=url`):
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "vc_2025-06-22_143045_789.wav",
      "url": "/outputs/vc_2025-06-22_143045_789.wav",
      "path": "/full/path/to/file.wav"
    }
  ],
  "processing_time_seconds": 15.43
}
```

### AudioFile Schema

| Field | Type | Description |
|-------|------|-------------|
| `format` | string | Audio format ("wav", "mp3", "flac") |
| `filename` | string | Generated filename |
| `url` | string | Relative URL for download |
| `path` | string | Full server file path (optional) |

## System Information Models

### HealthResponse

```json
{
  "status": "healthy",
  "models_loaded": {
    "tts_model": true,
    "voice_conversion_model": true,
    "whisper_model": true
  },
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "metrics": {
    "total_requests": 150,
    "successful_requests": 147,
    "failed_requests": 3,
    "avg_processing_time": 4.2
  },
  "system_info": {
    "python_version": "3.11.0",
    "torch_version": "2.0.0",
    "cuda_available": true,
    "gpu_memory_gb": 8.0
  },
  "resource_status": {
    "cpu_percent": 45.2,
    "memory_percent": 68.1,
    "disk_free_gb": 120.5
  },
  "warnings": [
    "GPU memory usage above 80%"
  ],
  "error_summary": {
    "total_errors": 3,
    "recent_errors": ["RESOURCE_NOT_FOUND", "INVALID_PARAMETERS"]
  }
}
```
### ConfigResponse

```json
{
  "tts_defaults": {
    "temperature": 0.75,
    "exaggeration": 0.5,
    "speed_factor": 1.0,
    "export_formats": ["wav", "mp3"]
  },
  "vc_defaults": {
    "chunk_sec": 60,
    "overlap_sec": 0.1,
    "export_formats": ["wav", "mp3"]
  },
  "supported_formats": ["wav", "mp3", "flac"],
  "api_limits": {
    "max_text_length": 10000,
    "max_file_size_mb": 100,
    "max_chunk_size_sec": 300
  }
}
```

### ErrorSummaryResponse

```json
{
  "total_errors": 25,
  "by_category": {
    "validation": 15,
    "resource": 8,
    "processing": 2
  },
  "by_severity": {
    "low": 20,
    "medium": 4,
    "high": 1
  },
  "by_operation": {
    "tts": 18,
    "vc": 5,
    "voice_upload": 2
  },
  "most_frequent": {
    "RESOURCE_NOT_FOUND": 8,
    "INVALID_PARAMETERS": 7,
    "FILE_TOO_LARGE": 3
  },
  "unresolved_count": 2,
  "recent_errors": [
    {
      "timestamp": "2025-06-22T14:30:00Z",
      "error_code": "RESOURCE_NOT_FOUND",
      "operation": "tts",
      "severity": "medium"
    }
  ]
}
```

## Voice Management Models

### VoiceMetadata

```json
{
  "name": "Professional Speaker",
  "description": "Clear, authoritative business voice",
  "duration_seconds": 12.5,
  "sample_rate": 22050,
  "file_size_bytes": 276480,
  "format": "wav",
  "default_parameters": {
    "temperature": 0.8,
    "speed_factor": 1.1
  },
  "tags": ["business", "professional", "clear"],
  "created_date": "2025-06-22T10:00:00Z",
  "last_used": "2025-06-22T14:30:22Z",
  "usage_count": 15,
  "folder_path": "corporate/executives"
}
```

### VoicesResponse

```json
{
  "voices": [
    {
      "name": "Speaker 1",
      "description": "Friendly narrator voice",
      "duration_seconds": 8.2,
      "sample_rate": 22050,
      "file_size_bytes": 181760,
      "format": "wav",
      "tags": ["narrator", "friendly"],
      "folder_path": "narrators"
    }
  ],
  "count": 25,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false
}
```

### VoiceUploadResponse

```json
{
  "success": true,
  "message": "Voice uploaded successfully",
  "voice_metadata": {
    "name": "New Speaker",
    "description": "Custom voice upload",
    "duration_seconds": 15.3,
    "file_size_bytes": 338688,
    "format": "wav",
    "tags": ["custom"],
    "created_date": "2025-06-22T14:45:00Z"
  },
  "filename": "new_speaker.wav"
}
```
### VoiceDeletionResponse

```json
{
  "success": true,
  "message": "Voice deleted successfully",
  "deleted_files": [
    "speaker1.wav",
    "speaker1.wav.json"
  ],
  "deleted_count": 2
}
```

### VoiceFoldersResponse

```json
{
  "folders": [
    {
      "path": "corporate/executives",
      "voice_count": 5,
      "subfolders": ["ceo", "managers"]
    },
    {
      "path": "narrators",
      "voice_count": 12,
      "subfolders": []
    }
  ],
  "total_folders": 8,
  "total_voices": 45
}
```

## Generated Files Models

### GeneratedFileMetadata

```json
{
  "filename": "tts_2025-06-22_143022_456.wav",
  "generation_type": "tts",
  "created_date": "2025-06-22T14:30:22Z",
  "file_size_bytes": 441000,
  "duration_seconds": 5.2,
  "format": "wav",
  "parameters": {
    "text": "Hello world",
    "temperature": 0.75,
    "speed_factor": 1.0,
    "reference_audio_filename": "test_voices/linda_johnson_02.mp3"
  },
  "source_files": ["speaker1.wav"],
  "folder_path": "outputs"
}
```

### GeneratedFilesResponse

```json
{
  "files": [
    {
      "filename": "tts_2025-06-22_143022_456.wav",
      "generation_type": "tts",
      "created_date": "2025-06-22T14:30:22Z",
      "file_size_bytes": 441000,
      "duration_seconds": 5.2
    }
  ],
  "count": 1,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false,
  "total_files": 25
}
```

## Response Headers

### Streaming Response Headers

| Header | Description | Example |
|--------|-------------|---------|
| `Content-Type` | Audio MIME type | `audio/wav` |
| `Content-Disposition` | Download filename | `attachment; filename="tts_123.wav"` |
| `Content-Length` | File size in bytes | `441000` |
| `X-Alternative-Formats` | Other format URLs | `mp3:/outputs/file.mp3\|flac:/outputs/file.flac` |
| `X-Processing-Time` | Generation time | `3.27` |
| `X-Generation-Seed` | Seed used | `42` |

### Standard Response Headers

| Header | Description | Example |
|--------|-------------|---------|
| `Content-Type` | Response format | `application/json` |
| `X-Request-ID` | Request tracking | `req_abc123def456` |
| `X-RateLimit-Remaining` | Requests remaining | `95` |
| `X-RateLimit-Reset` | Reset timestamp | `1703251200` |

## Pagination Structure

All paginated responses include:

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Items on current page |
| `page` | integer | Current page number |
| `page_size` | integer | Items per page |
| `total_pages` | integer | Total pages available |
| `has_next` | boolean | More pages available |
| `has_previous` | boolean | Previous pages available |
| `total_files` | integer | Total items (for files) |

### Pagination Example

```json
{
  "items": [...],
  "count": 25,
  "page": 2,
  "page_size": 25,
  "total_pages": 4,
  "has_next": true,
  "has_previous": true,
  "total_files": 87
}
```

## Error Response Details

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | Audio file not found |
| `INVALID_PARAMETERS` | 400 | Invalid request parameters |
| `UNSUPPORTED_FORMAT` | 400 | Unsupported audio format |
| `FILE_TOO_LARGE` | 413 | File exceeds size limit |
| `SERVICE_OVERLOADED` | 503 | Too many concurrent requests |
| `MODEL_LOADING_FAILED` | 500 | TTS/VC model initialization failed |
| `AUDIO_PROCESSING_ERROR` | 500 | Audio processing failed |
| `GENERATION_TIMEOUT` | 500 | Request processing timeout |

### Error Response Examples

**Resource Not Found**:
```json
{
  "success": false,
  "error": "Reference audio file not found: speaker1.wav",
  "error_code": "RESOURCE_NOT_FOUND",
  "detail": "Searched in: reference_audio/, reference_audio/tts_voices/",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

**Invalid Parameters**:
```json
{
  "success": false,
  "error": "Invalid temperature value. Must be between 0.1 and 1.5",
  "error_code": "INVALID_PARAMETERS",
  "detail": "temperature=2.0 exceeds maximum allowed value",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## Response Processing Tips

### Handling Stream Responses

```python
def handle_stream_response(response):
    """Process streaming audio response"""
    
    if response.status_code == 200:
        # Get metadata from headers
        filename = response.headers.get('Content-Disposition', '').split('filename=')[1].strip('"')
        content_type = response.headers.get('Content-Type')
        alt_formats = response.headers.get('X-Alternative-Formats', '')
        
        # Save audio file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return {
            'filename': filename,
            'content_type': content_type,
            'alternative_formats': parse_alt_formats(alt_formats)
        }
    else:
        # Handle error response
        error_data = response.json()
        raise APIError(error_data['error_code'], error_data['error'])
```

### Parsing Alternative Formats

```python
def parse_alt_formats(alt_formats_header):
    """Parse X-Alternative-Formats header"""
    
    if not alt_formats_header:
        return {}
    
    formats = {}
    for item in alt_formats_header.split('|'):
        if ':' in item:
            format_name, url = item.split(':', 1)
            formats[format_name] = url
    
    return formats

# Example: "mp3:/outputs/file.mp3|flac:/outputs/file.flac"
# Returns: {"mp3": "/outputs/file.mp3", "flac": "/outputs/file.flac"}
```

## See Also

- [Request Models](request-models.md) - API request schemas
- [Examples Collection](examples/) - Complete request/response examples  
- [Error Handling Guide](../guides/error-handling.md) - Error response handling
- [Streaming Responses Guide](../guides/streaming-responses.md) - Stream processing
- [Health Endpoint](../endpoints/health.md) - System status responses

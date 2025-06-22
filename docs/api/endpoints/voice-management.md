# Voice Management Endpoints

Upload, organize, and manage voice reference files for TTS and voice conversion.

## Overview

Voice management endpoints allow you to:
- Upload new voice reference files with metadata
- Organize voices in folders and with tags
- Update voice information without re-uploading files
- Delete individual or multiple voice files
- Browse voice library structure

## Upload Voice File

**POST** `/api/v1/voice`

Upload a new voice reference file with optional metadata and organization.

### Request Format

**Content-Type:** `multipart/form-data`

### Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `voice_file` | file | Yes | Voice audio file (WAV, MP3, FLAC) |
| `name` | string | No | Display name (defaults to filename) |
| `description` | string | No | Voice description |
| `tags` | string | No | Comma-separated tags |
| `folder_path` | string | No | Organization folder path |
| `default_parameters` | string | No | JSON string of default TTS parameters |
| `overwrite` | boolean | No | Overwrite existing file (default: false) |

### Example Requests

#### Basic Voice Upload

```bash
curl -X POST http://localhost:7860/api/v1/voice \
  -F "voice_file=@my_voice.wav" \
  -F "name=My Custom Voice" \
  -F "description=A professional speaking voice"
```

#### Advanced Upload with Organization

```bash
curl -X POST http://localhost:7860/api/v1/voice \
  -F "voice_file=@narrator.wav" \
  -F "name=Professional Narrator" \
  -F "description=Clear, authoritative voice for presentations" \
  -F "tags=professional,clear,narrator" \
  -F "folder_path=professional_voices" \
  -F 'default_parameters={"temperature": 0.8, "exaggeration": 0.3}'
```

### Response

```json
{
  "success": true,
  "message": "Voice uploaded successfully",
  "voice_info": {
    "filename": "my_voice.wav",
    "name": "My Custom Voice",
    "description": "A professional speaking voice",
    "folder_path": "professional_voices",
    "tags": ["professional", "clear", "narrator"],
    "file_size_bytes": 276480,
    "duration_seconds": 12.5,
    "sample_rate": 22050,
    "created_date": "2025-06-22T14:30:00Z"
  },
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## Update Voice Metadata

**PUT** `/api/v1/voice/{filename}/metadata`

Update voice metadata without changing the audio file.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Voice filename to update |

### Request Body (JSON)

```json
{
  "name": "Updated Voice Name",
  "description": "Updated description",
  "tags": ["tag1", "tag2", "tag3"],
  "default_parameters": {
    "temperature": 0.75,
    "exaggeration": 0.5
  }
}
```

### Example Request

```bash
curl -X PUT http://localhost:7860/api/v1/voice/my_voice.wav/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Professional Voice",
    "description": "Enhanced description with more details",
    "tags": ["professional", "updated", "clear"]
  }'
```

## Delete Single Voice

**DELETE** `/api/v1/voice/{filename}`

Delete a single voice file and its metadata.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Voice filename to delete |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `confirm` | boolean | Yes | Must be `true` for safety |

### Example Request

```bash
curl -X DELETE "http://localhost:7860/api/v1/voice/old_voice.wav?confirm=true"
```

### Response

```json
{
  "success": true,
  "message": "Voice file deleted successfully",
  "deleted_file": "old_voice.wav",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## Bulk Delete Voices

**DELETE** `/api/v1/voices`

Delete multiple voices based on criteria.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `confirm` | boolean | Yes | Must be `true` for safety |
| `folder` | string | No | Delete voices in specific folder |
| `tag` | string | No | Delete voices with specific tag |
| `search` | string | No | Delete voices matching search term |
| `filenames` | string | No | Comma-separated list of filenames |

### Example Requests

#### Delete by Folder

```bash
curl -X DELETE "http://localhost:7860/api/v1/voices?confirm=true&folder=test_voices"
```

#### Delete by Tag

```bash
curl -X DELETE "http://localhost:7860/api/v1/voices?confirm=true&tag=deprecated"
```

#### Delete Specific Files

```bash
curl -X DELETE "http://localhost:7860/api/v1/voices?confirm=true&filenames=voice1.wav,voice2.wav"
```

### Response

```json
{
  "success": true,
  "message": "Bulk delete completed",
  "deleted_count": 3,
  "deleted_files": ["voice1.wav", "voice2.wav", "voice3.wav"],
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## Get Voice Folder Structure

**GET** `/api/v1/voices/folders`

Get the voice library folder structure and organization.

### Response

```json
{
  "success": true,
  "folder_structure": {
    "root": {
      "voice_count": 5,
      "files": ["speaker1.wav", "speaker2.wav"]
    },
    "professional_voices": {
      "voice_count": 3,
      "files": ["narrator.wav", "presenter.wav", "formal.wav"]
    },
    "characters": {
      "voice_count": 4,
      "subfolders": {
        "protagonists": {
          "voice_count": 2,
          "files": ["hero.wav", "main_character.wav"]
        },
        "villains": {
          "voice_count": 2,
          "files": ["antagonist.wav", "dark_voice.wav"]
        }
      }
    }
  },
  "total_voices": 12,
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## List Available Voices

**GET** `/api/v1/voices`

List all available voices with metadata and pagination.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number for pagination |
| `page_size` | integer | 50 | Number of voices per page |
| `search` | string | - | Search term for voice names/descriptions |
| `folder` | string | - | Filter by folder path |
| `tag` | string | - | Filter by tag |
| `sort_by` | string | `"name"` | Sort by: `"name"`, `"created_date"`, `"duration"`, `"usage_count"` |
| `sort_order` | string | `"asc"` | Sort order: `"asc"` or `"desc"` |

### Example Requests

#### Basic Voice List

```bash
curl "http://localhost:7860/api/v1/voices?page=1&page_size=10"
```

#### Search and Filter

```bash
curl "http://localhost:7860/api/v1/voices?search=professional&folder=business_voices&sort_by=usage_count&sort_order=desc"
```

### Response

```json
{
  "success": true,
  "voices": [
    {
      "filename": "speaker1.wav",
      "name": "Professional Speaker 1",
      "description": "Clear, authoritative business voice",
      "folder_path": "business_voices",
      "tags": ["professional", "clear", "business"],
      "duration_seconds": 15.2,
      "file_size_bytes": 334080,
      "sample_rate": 22050,
      "created_date": "2025-06-20T10:00:00Z",
      "last_used": "2025-06-22T14:30:00Z",
      "usage_count": 25,
      "default_parameters": {
        "temperature": 0.8,
        "exaggeration": 0.3
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_voices": 45,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "timestamp": "2025-06-22T14:30:00Z"
}
```

## Python Examples

### Upload Voice with Metadata

```python
import requests

def upload_voice(file_path, name, description=None, tags=None, folder=None):
    with open(file_path, 'rb') as voice_file:
        files = {'voice_file': voice_file}
        data = {
            'name': name,
            'description': description or "",
            'tags': ','.join(tags) if tags else "",
            'folder_path': folder or ""
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/voice",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Voice uploaded: {result['voice_info']['filename']}")
        return result
    else:
        print(f"Upload failed: {response.status_code} - {response.text}")

# Usage
upload_voice(
    "my_voice.wav", 
    "My Professional Voice",
    description="Clear speaking voice for presentations",
    tags=["professional", "clear"],
    folder="business_voices"
)
```

### List and Search Voices

```python
import requests

def list_voices(search=None, folder=None, tag=None, page=1, page_size=20):
    params = {
        'page': page,
        'page_size': page_size
    }
    if search:
        params['search'] = search
    if folder:
        params['folder'] = folder
    if tag:
        params['tag'] = tag
    
    response = requests.get(
        "http://localhost:7860/api/v1/voices",
        params=params
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['pagination']['total_voices']} voices:")
        for voice in result['voices']:
            print(f"  {voice['name']} ({voice['filename']})")
        return result
    else:
        print(f"Failed to list voices: {response.status_code}")

# Usage examples
list_voices()  # List all voices
list_voices(search="professional")  # Search for professional voices
list_voices(folder="characters")  # List voices in characters folder
```

### Update Voice Metadata

```python
import requests

def update_voice_metadata(filename, name=None, description=None, tags=None):
    payload = {}
    if name:
        payload['name'] = name
    if description:
        payload['description'] = description
    if tags:
        payload['tags'] = tags
    
    response = requests.put(
        f"http://localhost:7860/api/v1/voice/{filename}/metadata",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"Metadata updated for {filename}")
        return response.json()
    else:
        print(f"Update failed: {response.status_code} - {response.text}")

# Usage
update_voice_metadata(
    "speaker1.wav",
    name="Updated Speaker Name",
    description="Enhanced description",
    tags=["professional", "updated"]
)
```

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "Voice file already exists",
  "detail": "Use overwrite=true to replace existing file",
  "error_code": "FILE_EXISTS",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

### Error Types

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `FILE_EXISTS` | 409 | Voice file already exists | Use `overwrite=true` parameter |
| `FILE_NOT_FOUND` | 404 | Voice file not found | Check filename and path |
| `INVALID_AUDIO` | 400 | Invalid audio file format | Use WAV, MP3, or FLAC |
| `FILE_TOO_LARGE` | 413 | Audio file exceeds size limit | Use smaller audio files |
| `VALIDATION_ERROR` | 400 | Invalid request parameters | Check parameter formats |
| `PERMISSION_DENIED` | 403 | Cannot delete/modify file | Check file permissions |

## File Organization

### Voice Directory Structure

Voice files are organized in the `reference_audio/` directory:

```
reference_audio/
├── speaker1.wav                    # Root level voices
├── speaker2.wav
├── business_voices/                # Organized by purpose
│   ├── formal_presenter.wav
│   ├── casual_speaker.wav
│   └── narrator.wav
├── characters/                     # Organized by content type
│   ├── protagonists/
│   │   ├── hero_voice.wav
│   │   └── main_character.wav
│   └── villains/
│       ├── antagonist.wav
│       └── dark_voice.wav
└── languages/                      # Organized by language
    ├── english/
    │   ├── american_accent.wav
    │   └── british_accent.wav
    └── spanish/
        └── native_speaker.wav
```

### Metadata Files

Each voice can have an associated metadata file:

```
reference_audio/
├── speaker1.wav
├── speaker1.wav.json              # Metadata companion file
├── business_voices/
│   ├── formal_presenter.wav
│   └── formal_presenter.wav.json  # Metadata for this voice
```

## Best Practices

### Voice Quality Guidelines

1. **Duration**: 10-30 seconds of clear speech
2. **Content**: Natural conversation, avoid reading style
3. **Quality**: High sample rate (22kHz+), minimal background noise
4. **Speaker**: Single speaker, consistent voice characteristics

### Organization Tips

1. **Use descriptive names**: "Professional_Female_Narrator" vs "voice1"
2. **Consistent tagging**: Use standard tags across similar voices
3. **Folder structure**: Group by purpose, character, or language
4. **Regular cleanup**: Remove unused or poor-quality voices

### Metadata Best Practices

1. **Meaningful descriptions**: Help users understand voice characteristics
2. **Relevant tags**: Make voices discoverable
3. **Default parameters**: Set optimal TTS settings per voice
4. **Regular updates**: Keep usage statistics current

## Related Endpoints

- **[TTS Endpoint](tts.md)** - Use uploaded voices for speech generation
- **[Voice Conversion](voice-conversion.md)** - Use voices as conversion targets
- **[File Operations](file-operations.md)** - Manage generated files

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*

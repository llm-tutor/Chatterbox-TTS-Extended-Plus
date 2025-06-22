# Voice Conversion (VC) Endpoint

Convert voice characteristics of input audio to match a target voice with support for direct file uploads and streaming response.

## Endpoint

**POST** `/api/v1/vc`

Transform the voice characteristics of input audio to sound like a different target speaker while preserving the original speech content.

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `response_mode` | string | `"stream"` | Response mode: `"stream"` for direct file download, `"url"` for JSON response |
| `return_format` | string | first from export_formats | Format to stream: `"wav"`, `"mp3"`, `"flac"` |

## Request Methods

Voice conversion supports two input methods depending on your use case:

### Method 1: JSON Request with File References

**Content-Type:** `application/json`

Use this method when input files are already stored on the server.

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_audio_source` | string | Source audio filename in `vc_inputs/` directory or URL |
| `target_voice_source` | string | Target voice filename in `reference_audio/` directory or URL |

#### Optional Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `chunk_sec` | integer | 60 | 10-300 | Chunk duration in seconds for processing |
| `overlap_sec` | float | 0.1 | 0.0-2.0 | Overlap between chunks for seamless joining |
| `export_formats` | array | `["wav","mp3"]` | - | Output formats: `"wav"`, `"mp3"`, `"flac"` |
| `disable_watermark` | boolean | true | - | Disable audio watermarking |

#### Example Request

```json
{
  "input_audio_source": "recording.wav",
  "target_voice_source": "speaker2.wav",
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "export_formats": ["wav", "mp3"]
}
```

### Method 2: Direct File Upload (Multipart)

**Content-Type:** `multipart/form-data`

Use this method to upload input audio files directly without pre-staging.

#### Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_audio` | file | Yes | Input audio file (max 100MB) |
| `target_voice_source` | string | Yes | Target voice filename in `reference_audio/` |
| `chunk_sec` | integer | No | Chunk size in seconds (default: 60) |
| `overlap_sec` | float | No | Overlap in seconds (default: 0.1) |
| `export_formats` | string | No | Comma-separated formats (default: "wav,mp3") |
| `disable_watermark` | boolean | No | Disable watermark (default: true) |

#### Example cURL with File Upload

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -F "input_audio=@my_recording.wav" \
  -F "target_voice_source=celebrity_voice.wav" \
  -F "chunk_sec=30" \
  -F "export_formats=wav,mp3"
```

## Method Comparison

| Aspect | JSON Request | File Upload |
|--------|--------------|-------------|
| **Input Audio** | Must exist in `vc_inputs/` | Upload directly in request |
| **Target Voice** | Must exist in `reference_audio/` | Must exist in `reference_audio/` |
| **File Size** | No server limit | Max 100MB per upload |
| **Use Case** | Server-side files, automation | Client apps, web interfaces |
| **Pre-staging** | Required | Not required |

## Response Formats

### Streaming Response (default)

When `response_mode="stream"` (default), returns the audio file directly:

```
HTTP/1.1 200 OK
Content-Type: audio/wav
Content-Disposition: attachment; filename="vc_2025-06-22_143045_789_chunk60_overlap0.1.wav"
X-Alternative-Formats: mp3:/outputs/vc_2025-06-22_143045_789_chunk60_overlap0.1.mp3

[Binary audio data]
```

The `X-Alternative-Formats` header contains URLs to other generated formats.

### JSON Response

When `response_mode="url"`, returns JSON with file information:

```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.wav",
      "url": "/outputs/vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.wav",
      "path": "/path/to/outputs/vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.wav"
    },
    {
      "format": "mp3",
      "filename": "vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.mp3",
      "url": "/outputs/vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.mp3",
      "path": "/path/to/outputs/vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.mp3"
    }
  ],
  "processing_time_seconds": 8.7,
  "message": "Voice conversion completed successfully",
  "timestamp": "2025-06-22T14:30:45Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success status |
| `output_files` | array | Generated audio file information |
| `processing_time_seconds` | float | Total processing time |
| `message` | string | Success message |
| `timestamp` | string | ISO 8601 response timestamp |

## Usage Examples

### cURL Examples

#### JSON Request with Local Files

```bash
curl -X POST http://localhost:7860/api/v1/vc?response_mode=url \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "my_recording.wav",
    "target_voice_source": "target_voices/celebrity.wav",
    "chunk_sec": 30,
    "export_formats": ["wav"]
  }'
```

#### JSON Request with URL Input

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "https://example.com/speech.wav",
    "target_voice_source": "speaker2/style.wav",
    "export_formats": ["wav", "mp3"]
  }' \
  --output converted_voice.wav
```

#### File Upload with Streaming Response

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -F "input_audio=@/path/to/recording.wav" \
  -F "target_voice_source=celebrity_voice.wav" \
  -F "chunk_sec=45" \
  -F "export_formats=wav" \
  --output converted_output.wav
```

### Python Examples

#### JSON Request Method

```python
import requests

def convert_voice_json(input_file, target_voice, chunk_size=60):
    payload = {
        "input_audio_source": input_file,
        "target_voice_source": target_voice,
        "chunk_sec": chunk_size,
        "export_formats": ["wav", "mp3"]
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/vc?response_mode=url",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Conversion completed in {result['processing_time_seconds']:.1f}s")
        for file_info in result['output_files']:
            print(f"  {file_info['format']}: {file_info['url']}")
        return result
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
convert_voice_json("recording.wav", "target_voice.wav")
```

#### File Upload Method

```python
import requests

def convert_voice_upload(audio_file_path, target_voice, chunk_size=60):
    with open(audio_file_path, 'rb') as audio_file:
        files = {'input_audio': audio_file}
        data = {
            'target_voice_source': target_voice,
            'chunk_sec': chunk_size,
            'export_formats': 'wav,mp3'
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/vc?response_mode=url",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Upload and conversion completed: {result['message']}")
        return result
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
convert_voice_upload("/path/to/audio.wav", "celebrity_voice.wav")
```

#### Direct Download Method

```python
import requests

def download_converted_voice(audio_file_path, target_voice, output_path):
    with open(audio_file_path, 'rb') as audio_file:
        files = {'input_audio': audio_file}
        data = {
            'target_voice_source': target_voice,
            'export_formats': 'wav'
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/vc",
            files=files,
            data=data,
            stream=True
        )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded converted audio: {output_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
download_converted_voice("input.wav", "target.wav", "converted.wav")
```

### JavaScript Examples

#### File Upload in Browser

```javascript
async function convertVoiceUpload(audioFile, targetVoice, options = {}) {
    const formData = new FormData();
    formData.append('input_audio', audioFile);
    formData.append('target_voice_source', targetVoice);
    formData.append('chunk_sec', options.chunkSize || 60);
    formData.append('export_formats', options.formats || 'wav,mp3');
    
    const url = options.responseMode === 'url' 
        ? 'http://localhost:7860/api/v1/vc?response_mode=url'
        : 'http://localhost:7860/api/v1/vc';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (options.responseMode === 'url') {
            const data = await response.json();
            console.log('Conversion completed:', data.output_files);
            return data;
        } else {
            const blob = await response.blob();
            const downloadUrl = URL.createObjectURL(blob);
            console.log('Download URL created:', downloadUrl);
            return downloadUrl;
        }
    } catch (error) {
        console.error('Voice conversion failed:', error);
    }
}

// Usage with file input
document.getElementById('audioFile').addEventListener('change', (event) => {
    const file = event.target.files[0];
    convertVoiceUpload(file, 'celebrity_voice.wav', { responseMode: 'url' });
});
```

## Processing Details

### Chunking Strategy

Voice conversion processes long audio files in chunks to manage memory and ensure quality:

1. **Input audio is split** into chunks of specified duration (`chunk_sec`)
2. **Each chunk is processed** independently with the target voice
3. **Overlapping regions** (`overlap_sec`) ensure seamless transitions
4. **Chunks are rejoined** to create the final output

### Optimal Chunk Sizes

| Audio Length | Recommended Chunk Size | Reasoning |
|--------------|----------------------|-----------|
| < 2 minutes | 60 seconds | Single chunk, no splitting |
| 2-10 minutes | 30-45 seconds | Balance quality and memory |
| > 10 minutes | 20-30 seconds | Prevent memory issues |

### Processing Time Estimates

| Audio Length | Typical Processing Time | Notes |
|--------------|----------------------|-------|
| 30 seconds | 15-30 seconds | Single chunk |
| 2 minutes | 45-90 seconds | 2-4 chunks |
| 5 minutes | 2-4 minutes | Multiple chunks |
| 10+ minutes | 0.4-0.8x audio length | Depends on chunk size |

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "Input audio file is required",
  "detail": "No input audio provided via file upload or source parameter",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-22T14:30:45Z"
}
```

### Error Types

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `VALIDATION_ERROR` | 400 | Missing or invalid parameters | Check required fields |
| `FILE_NOT_FOUND` | 404 | Audio files not found | Verify file paths and existence |
| `FILE_TOO_LARGE` | 413 | Upload exceeds size limit | Use smaller files or JSON method |
| `UNSUPPORTED_FORMAT` | 400 | Audio format not supported | Use WAV, MP3, or FLAC |
| `PROCESSING_ERROR` | 500 | Voice conversion failed | Try different chunk size or retry |

## File Organization

### Input Files for JSON Method

Place input audio files in the `vc_inputs/` directory:

```
vc_inputs/
├── recording1.wav
├── meeting_audio.mp3
├── podcasts/
│   ├── episode1.wav
│   └── episode2.mp3
└── personal/
    └── speech_practice.wav
```

### Target Voice Files

Place target voice references in the `reference_audio/` directory:

```
reference_audio/
├── celebrity_voice.wav
├── professional_speaker.wav
├── characters/
│   ├── protagonist.wav
│   └── narrator.wav
└── styles/
    ├── formal.wav
    └── casual.wav
```

### Generated Output Files

Voice conversion output files include processing parameters in the filename:

```
outputs/
├── vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.wav
├── vc_2025-06-22_143045_789_chunk60_overlap0.1_voicespeaker2.mp3
└── vc_2025-06-22_143100_123_chunk30_overlap0.2_voicecelebrity.wav
```

## Performance Tips

### Optimization Strategies

1. **Choose appropriate chunk size**: Balance quality and processing time
2. **Use optimal overlap**: 0.1-0.2 seconds usually sufficient
3. **Select efficient formats**: WAV for quality, MP3 for size
4. **Pre-process audio**: Clean input audio improves results
5. **Use quality target voices**: 10-30 seconds of clear speech

### Quality Recommendations

#### Input Audio Requirements
- **Sample rate**: 16kHz, 22kHz, or 44.1kHz
- **Format**: WAV (best), MP3, or FLAC
- **Quality**: Clear speech, minimal background noise
- **Length**: Any length (chunking handles long files)

#### Target Voice Requirements
- **Duration**: 10-30 seconds of clear speech
- **Content**: Natural, conversational speech
- **Quality**: High-quality recording, no noise
- **Speaker**: Single speaker, consistent voice

## Related Endpoints

- **[Voice Management](voice-management.md)** - Upload and manage target voices
- **[File Operations](file-operations.md)** - List and download generated files
- **[TTS Endpoint](tts.md)** - Text-to-speech generation

## Advanced Features

- **[File Uploads](../guides/file-uploads.md)** - Detailed upload handling
- **[Streaming Responses](../guides/streaming-responses.md)** - Direct file downloads
- **[Advanced Features](../guides/advanced-features.md)** - Processing optimization

## Troubleshooting

### Common Issues

**Poor Conversion Quality**
- Use higher quality target voice
- Reduce chunk size for better processing
- Ensure input audio is clear

**Processing Takes Too Long**
- Increase chunk size
- Use shorter target voice samples
- Check system resources

**Memory Errors**
- Reduce chunk size
- Process shorter audio segments
- Check available RAM

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*

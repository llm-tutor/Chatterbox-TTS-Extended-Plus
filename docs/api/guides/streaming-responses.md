# Streaming Responses Guide

> **Chatterbox TTS Extended Plus** - Direct file downloads for seamless integration

## Overview

The Chatterbox TTS API supports two response modes:
- **Stream Mode** (default): Direct audio file download
- **JSON Mode**: Traditional URL-based response

Stream mode provides a better user experience by eliminating the two-step process of generate → download.

## How It Works

### Default Behavior (Stream Mode)
When you make a request without specifying `response_mode`, the API streams the audio file directly:

```bash
# Direct audio download (default)
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav"]}' \
  --output speech.wav
```

### JSON Mode (Legacy)
Use `response_mode=url` to get URLs instead of direct files:

```bash
# Get JSON response with URLs
curl -X POST "http://localhost:7860/api/v1/tts?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav"]}'
```

## Response Headers

### Stream Mode Headers
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="tts_2025-06-22_143022_456.wav"
X-Alternative-Formats: mp3:/outputs/file.mp3|flac:/outputs/file.flac
```

### Multiple Format Support
When multiple formats are requested, the primary format is streamed directly:
- The first format in `export_formats` is streamed
- Other formats are available via `X-Alternative-Formats` header

## Programming Examples

### Python - Direct Download
```python
import requests

def download_tts_direct(text, output_path="speech.wav"):
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json={"text": text, "export_formats": ["wav"]},
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {output_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
download_tts_direct("Hello world", "my_speech.wav")
```

### Python - JSON Mode (Legacy)
```python
import requests

def get_tts_urls(text):
    response = requests.post(
        "http://localhost:7860/api/v1/tts?response_mode=url",
        json={"text": text, "export_formats": ["wav", "mp3"]}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['output_files']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Usage
urls = get_tts_urls("Hello world")
print(f"Generated files: {urls}")
```

### JavaScript - Fetch API
```javascript
async function downloadTTSAudio(text, outputFilename = 'speech.wav') {
    try {
        const response = await fetch('http://localhost:7860/api/v1/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                export_formats: ['wav']
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Create download link
            const a = document.createElement('a');
            a.href = url;
            a.download = outputFilename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            return blob;
        } else {
            const error = await response.text();
            console.error(`Error ${response.status}: ${error}`);
        }
    } catch (error) {
        console.error('Download failed:', error);
    }
}

// Usage
downloadTTSAudio("Hello world", "my_speech.wav");
```

## Voice Conversion Support

Voice conversion also supports streaming responses:

```bash
# Stream VC result directly
curl -X POST http://localhost:7860/api/v1/vc \
  -F "input_audio=@my_recording.wav" \
  -F "target_voice_source=speaker1.wav" \
  --output converted_audio.wav
```

## Best Practices

### 1. Use Stream Mode for Direct Integration
Stream mode is ideal for:
- Desktop applications
- Command-line tools
- Direct file processing workflows

### 2. Use JSON Mode for Web Applications
JSON mode may be better for:
- Web apps that need to display progress
- Applications that need file URLs for sharing
- Systems that process multiple formats differently

### 3. Handle Large Files Properly
For large audio files, always use streaming:
```python
# Good: Stream large responses
response = requests.post(url, json=data, stream=True)
with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

# Avoid: Loading entire file into memory
response = requests.post(url, json=data)
with open(output_path, 'wb') as f:
    f.write(response.content)  # Don't do this for large files
```

### 4. Check Alternative Formats
When multiple formats are requested:
```python
# Get alternative format URLs from headers
alt_formats_header = response.headers.get('X-Alternative-Formats', '')
if alt_formats_header:
    formats = dict(item.split(':') for item in alt_formats_header.split('|'))
    mp3_url = formats.get('mp3')
    flac_url = formats.get('flac')
```

## Error Handling

Stream mode returns standard HTTP error codes:

```python
def handle_streaming_response(response):
    if response.status_code == 200:
        # Success - process the audio stream
        return process_audio_stream(response)
    elif response.status_code == 400:
        # Bad request - check your parameters
        error_detail = response.text
        print(f"Invalid request: {error_detail}")
    elif response.status_code == 404:
        # File not found - check reference audio paths
        print("Reference audio file not found")
    elif response.status_code == 503:
        # Service unavailable - model loading failed
        print("TTS service temporarily unavailable")
    else:
        print(f"Unexpected error {response.status_code}: {response.text}")
```

## Migration from JSON Mode

If you're updating from JSON-only responses:

### Before (JSON Mode)
```python
# Old approach - two requests
response = requests.post(url, json=data)
result = response.json()
file_url = result['output_files'][0]['url']

# Second request to download
audio_response = requests.get(file_url)
with open('output.wav', 'wb') as f:
    f.write(audio_response.content)
```

### After (Stream Mode)
```python
# New approach - single request
response = requests.post(url, json=data, stream=True)
with open('output.wav', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

## See Also

- [File Uploads Guide](file-uploads.md) - For uploading source audio
- [Error Handling Guide](error-handling.md) - Comprehensive error handling
- [TTS Endpoint](../endpoints/tts.md) - Complete TTS API reference
- [Voice Conversion Endpoint](../endpoints/voice-conversion.md) - Complete VC API reference

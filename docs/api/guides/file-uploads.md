# File Uploads Guide

> **Chatterbox TTS Extended Plus** - Direct file upload capabilities for voice conversion

## Overview

The Chatterbox TTS API supports multiple ways to provide audio files:
- **Direct Upload**: Upload files in the request (multipart/form-data)
- **Server Files**: Reference files already on the server
- **URL Sources**: Download from external URLs

This guide focuses on direct file uploads for maximum flexibility.

## Supported Upload Scenarios

### Voice Conversion
- **Input Audio**: Upload source audio to be converted
- **Target Voice**: Reference existing voice files on server

### Voice Management  
- **Voice Files**: Upload new reference voices with metadata
- **Bulk Upload**: Multiple voice files with organization

## File Upload Methods

### 1. Voice Conversion with Upload

Upload your source audio directly in the request:

```bash
curl -X POST http://localhost:7860/api/v1/vc \
  -F "input_audio=@my_recording.wav" \
  -F "target_voice_source=speaker1.wav" \
  -F "chunk_sec=30" \
  --output converted_audio.wav
```

### 2. Voice Management Upload

Upload new reference voices:

```bash
curl -X POST http://localhost:7860/api/v1/voice \
  -F "audio_file=@new_speaker.wav" \
  -F "metadata={\"name\":\"Professional Speaker\",\"description\":\"Clear, authoritative voice\"}" \
  -F "folder_path=business/presenters"
```

## Programming Examples

### Python - Voice Conversion Upload

```python
import requests

def convert_uploaded_audio(input_file_path, target_voice, output_path):
    """Convert uploaded audio using target voice from server"""
    
    with open(input_file_path, 'rb') as audio_file:
        files = {
            'input_audio': audio_file
        }
        data = {
            'target_voice_source': target_voice,
            'chunk_sec': 60,
            'overlap_sec': 0.1
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
                    if chunk:
                        f.write(chunk)
            print(f"Converted and downloaded: {output_path}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False

# Usage
convert_uploaded_audio(
    "my_recording.wav", 
    "celebrity_voice.wav", 
    "converted_output.wav"
)
```

### Python - Voice Upload

```python
import requests
import json

def upload_voice_file(audio_path, voice_name, description="", folder_path=""):
    """Upload a new reference voice file"""
    
    with open(audio_path, 'rb') as audio_file:
        files = {
            'audio_file': audio_file
        }
        
        metadata = {
            'name': voice_name,
            'description': description,
            'tags': ['uploaded', 'custom']
        }
        
        data = {
            'metadata': json.dumps(metadata),
            'folder_path': folder_path
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/voice",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Voice uploaded successfully: {result['filename']}")
            return result
        else:
            print(f"Upload failed {response.status_code}: {response.text}")
            return None

# Usage
upload_voice_file(
    "speaker_recording.wav",
    "CEO Voice",
    "Authoritative business speaker",
    "corporate/executives"
)
```

### JavaScript - Voice Conversion Upload

```javascript
async function uploadAndConvertAudio(inputFile, targetVoice, outputFilename) {
    const formData = new FormData();
    formData.append('input_audio', inputFile);
    formData.append('target_voice_source', targetVoice);
    formData.append('chunk_sec', '60');
    
    try {
        const response = await fetch('http://localhost:7860/api/v1/vc', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = outputFilename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            console.log('Conversion completed and downloaded');
            return blob;
        } else {
            const error = await response.text();
            console.error(`Conversion failed: ${error}`);
        }
    } catch (error) {
        console.error('Upload failed:', error);
    }
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        await uploadAndConvertAudio(file, 'speaker1.wav', 'converted.wav');
    }
});
```

## File Format Support

### Supported Input Formats
- **WAV**: Uncompressed audio (preferred)
- **MP3**: Compressed audio (automatically decoded)
- **FLAC**: Lossless compression
- **M4A**: AAC container format
- **OGG**: Ogg Vorbis

### Audio Requirements
- **Sample Rate**: Any (automatically resampled to 22050 Hz)
- **Channels**: Mono or Stereo (converted to mono if needed)
- **Bit Depth**: Any (converted to 16-bit)
- **Duration**: Recommended 5-300 seconds for reference voices

## Form Data Structure

### Voice Conversion Upload
```
Content-Type: multipart/form-data

Fields:
- input_audio: [binary file data]
- target_voice_source: "speaker1.wav"
- chunk_sec: 60
- overlap_sec: 0.1
- export_formats: ["wav", "mp3"]
```

### Voice Management Upload
```
Content-Type: multipart/form-data

Fields:
- audio_file: [binary file data]
- metadata: '{"name":"Speaker Name","description":"..."}'
- folder_path: "category/subcategory"
```

## File Size Limits

### Current Limits
- **Maximum File Size**: 100MB per upload
- **Recommended Size**: Under 10MB for optimal processing
- **Voice Reference**: 5-30 seconds (1-5MB typical)

### Large File Handling
For large files, consider:
1. **Audio compression**: Use MP3 or FLAC before upload
2. **Chunking**: Split long audio into segments
3. **Server placement**: Use server file references for frequently used files

## Validation and Processing

### Automatic Processing
The server automatically:
- Validates audio format
- Resamples to 22050 Hz
- Converts to mono if stereo
- Normalizes audio levels

### Upload Validation
```python
def validate_upload_response(response):
    """Validate upload response and extract key information"""
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Upload successful")
        print(f"  Filename: {result.get('filename')}")
        print(f"  Duration: {result.get('duration_seconds', 'N/A')}s")
        print(f"  File size: {result.get('file_size_bytes', 'N/A')} bytes")
        return result
        
    elif response.status_code == 400:
        error = response.json()
        if 'UNSUPPORTED_FORMAT' in error.get('error_code', ''):
            print("✗ Unsupported audio format")
        elif 'FILE_TOO_LARGE' in error.get('error_code', ''):
            print("✗ File exceeds size limit")
        else:
            print(f"✗ Upload error: {error.get('error_message')}")
        return None
        
    else:
        print(f"✗ Server error {response.status_code}: {response.text}")
        return None
```

## Security Considerations

### File Type Validation
- Only audio files are accepted
- File content is validated, not just extension
- Potentially malicious files are rejected

### Path Safety
- Folder paths are sanitized
- No directory traversal allowed
- Files are stored in designated upload areas

### Size Limits
- Prevents resource exhaustion
- Protects against abuse
- Configurable per deployment

## Troubleshooting Uploads

### Common Upload Issues

**1. "Unsupported file format"**
```bash
# Check file format
file my_audio.wav
# Output: my_audio.wav: RIFF (little-endian) data, WAVE audio

# Convert if needed
ffmpeg -i input.m4a -ar 22050 -ac 1 output.wav
```

**2. "File too large"**
```bash
# Check file size
ls -lh my_audio.wav

# Compress if needed
ffmpeg -i input.wav -b:a 128k output.mp3
```

**3. "Upload timeout"**
```python
# Increase timeout for large files
response = requests.post(
    url, 
    files=files, 
    data=data, 
    timeout=300  # 5 minutes
)
```

### Network Issues
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_retry_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Use for reliable uploads
session = create_retry_session()
response = session.post(url, files=files, data=data)
```

## Performance Tips

### 1. Optimize Audio Before Upload
```bash
# Optimal format for upload (small size, good quality)
ffmpeg -i input.wav -ar 22050 -ac 1 -b:a 128k output.mp3
```

### 2. Use Progress Tracking
```python
from tqdm import tqdm
import requests

class UploadProgress:
    def __init__(self, filename):
        self.filename = filename
        self.pbar = None
        
    def __call__(self, monitor):
        if self.pbar is None:
            self.pbar = tqdm(total=monitor.len, unit='B', unit_scale=True)
            self.pbar.set_description(f"Uploading {self.filename}")
        self.pbar.update(monitor.bytes_read - self.pbar.n)

# Usage with progress bar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

with open(file_path, 'rb') as f:
    encoder = MultipartEncoder(fields={'input_audio': (filename, f, 'audio/wav')})
    monitor = MultipartEncoderMonitor(encoder, UploadProgress(filename))
    
    response = requests.post(
        url,
        data=monitor,
        headers={'Content-Type': monitor.content_type}
    )
```

### 3. Batch Operations
For multiple files, consider server-side placement:
```python
# Better: Upload once, use multiple times
upload_voice_file("speaker.wav", "Speaker 1")

# Then reference by filename
requests.post("/api/v1/tts", json={
    "text": "Hello world",
    "reference_audio_filename": "speaker.wav"
})
```

## See Also

- [Streaming Responses Guide](streaming-responses.md) - Downloading generated audio
- [Error Handling Guide](error-handling.md) - Upload error handling
- [Voice Conversion Endpoint](../endpoints/voice-conversion.md) - Complete VC API
- [Voice Management Endpoint](../endpoints/voice-management.md) - Voice upload API
- [File Structure Reference](../reference/file-structure.md) - Server directory organization

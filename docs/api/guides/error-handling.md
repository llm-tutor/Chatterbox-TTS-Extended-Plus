# Error Handling Guide

> **Chatterbox TTS Extended Plus** - Comprehensive error handling and troubleshooting

## Overview

The Chatterbox TTS API provides detailed error information to help developers quickly identify and resolve issues. This guide covers all error scenarios and provides practical solutions.

## Error Response Format

### Standard Error Structure
```json
{
  "success": false,
  "error_message": "Human-readable error description",
  "error_code": "MACHINE_READABLE_CODE",
  "detail": "Technical details for debugging",
  "request_id": "unique-request-identifier",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters or request format |
| 404 | Not Found | Referenced files or endpoints missing |
| 413 | Payload Too Large | File upload exceeds size limits |
| 422 | Unprocessable Entity | Valid format but semantic errors |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Model loading failed or overloaded |
## Error Categories

### 1. Request Validation Errors (400)

**INVALID_PARAMETERS**
```json
{
  "success": false,
  "error_message": "Invalid temperature value. Must be between 0.1 and 1.5",
  "error_code": "INVALID_PARAMETERS",
  "detail": "temperature=2.0 exceeds maximum allowed value"
}
```

**MISSING_REQUIRED_FIELD**
```json
{
  "success": false,
  "error_message": "Required field 'text' is missing",
  "error_code": "MISSING_REQUIRED_FIELD",
  "detail": "TTS requests must include text field"
}
```

**UNSUPPORTED_FORMAT**
```json
{
  "success": false,
  "error_message": "Unsupported audio format: .avi",
  "error_code": "UNSUPPORTED_FORMAT",
  "detail": "Supported formats: wav, mp3, flac, m4a, ogg"
}
```
### 2. Resource Errors (404)

**RESOURCE_NOT_FOUND**
```json
{
  "success": false,
  "error_message": "Reference audio file not found: speaker1.wav",
  "error_code": "RESOURCE_NOT_FOUND",
  "detail": "Searched in: reference_audio/, reference_audio/tts_voices/"
}
```

**VOICE_NOT_FOUND**
```json
{
  "success": false,
  "error_message": "Voice file 'missing_speaker.wav' not found in reference directory",
  "error_code": "VOICE_NOT_FOUND",
  "detail": "Available voices: speaker1.wav, narrator.wav, presenter.wav"
}
```

### 3. Processing Errors (500)

**MODEL_LOADING_FAILED**
```json
{
  "success": false,
  "error_message": "Failed to load TTS model",
  "error_code": "MODEL_LOADING_FAILED",
  "detail": "CUDA out of memory. Try reducing batch size or using CPU mode."
}
```
**AUDIO_PROCESSING_ERROR**
```json
{
  "success": false,
  "error_message": "Failed to process audio file",
  "error_code": "AUDIO_PROCESSING_ERROR",
  "detail": "Corrupted audio data or unsupported codec"
}
```

**GENERATION_TIMEOUT**
```json
{
  "success": false,
  "error_message": "Audio generation timed out",
  "error_code": "GENERATION_TIMEOUT",
  "detail": "Processing exceeded 300 seconds. Try shorter text or smaller chunk size."
}
```

### 4. Resource Limit Errors (413, 503)

**FILE_TOO_LARGE**
```json
{
  "success": false,
  "error_message": "Uploaded file exceeds 100MB limit",
  "error_code": "FILE_TOO_LARGE",
  "detail": "File size: 150MB. Maximum allowed: 100MB"
}
```

**SERVICE_OVERLOADED**
```json
{
  "success": false,
  "error_message": "Service temporarily overloaded",
  "error_code": "SERVICE_OVERLOADED",
  "detail": "Too many concurrent requests. Retry after 30 seconds."
}
```
## Programming Error Handling

### Python - Comprehensive Error Handling

```python
import requests
import time
import logging

class ChatterboxAPIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, status_code, error_code, message, detail=None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail
        super().__init__(f"{error_code}: {message}")

class ChatterboxClient:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def _handle_response(self, response):
        """Handle API response with proper error handling"""
        
        if response.status_code == 200:
            return response
            
        # Try to parse error JSON
        try:
            error_data = response.json()
            error_code = error_data.get('error_code', 'UNKNOWN_ERROR')
            error_message = error_data.get('error_message', 'Unknown error occurred')
            detail = error_data.get('detail')
        except ValueError:
            # Non-JSON error response
            error_code = f"HTTP_{response.status_code}"
            error_message = response.text or "No error message provided"
            detail = None
        
        raise ChatterboxAPIError(
            status_code=response.status_code,
            error_code=error_code,
            message=error_message,
            detail=detail
        )
```    
    def generate_tts(self, text, reference_audio=None, **kwargs):
        """Generate TTS with comprehensive error handling"""
        
        payload = {"text": text, **kwargs}
        if reference_audio:
            payload["reference_audio_filename"] = reference_audio
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/tts",
                json=payload,
                stream=True,
                timeout=300
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError:
            raise ChatterboxAPIError(
                status_code=0,
                error_code="CONNECTION_ERROR",
                message="Cannot connect to Chatterbox TTS server",
                detail="Check if server is running and accessible"
            )
        except requests.exceptions.Timeout:
            raise ChatterboxAPIError(
                status_code=0,
                error_code="REQUEST_TIMEOUT",
                message="Request timed out",
                detail="Server may be overloaded or processing large request"
            )
    
    def generate_with_retry(self, text, max_retries=3, **kwargs):
        """Generate TTS with automatic retry logic"""
        
        for attempt in range(max_retries + 1):
            try:
                return self.generate_tts(text, **kwargs)
                
            except ChatterboxAPIError as e:
                # Don't retry for permanent errors
                if e.error_code in ['RESOURCE_NOT_FOUND', 'INVALID_PARAMETERS', 'UNSUPPORTED_FORMAT']:
                    raise
                
                # Retry for temporary errors
                if attempt < max_retries and e.error_code in ['SERVICE_OVERLOADED', 'MODEL_LOADING_FAILED']:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e.message}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Max retries exceeded
                raise
```
# Usage example
client = ChatterboxClient()

try:
    response = client.generate_with_retry(
        "Hello world",
        reference_audio_filename="speaker1.wav",
        temperature=0.8
    )
    
    # Save audio file
    with open("output.wav", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print("TTS generation successful!")
    
except ChatterboxAPIError as e:
    print(f"TTS failed: {e.message}")
    if e.detail:
        print(f"Details: {e.detail}")
    
    # Handle specific error types
    if e.error_code == "RESOURCE_NOT_FOUND":
        print("Check that reference audio file exists in reference_audio/ directory")
    elif e.error_code == "INVALID_PARAMETERS":
        print("Review parameter values and try again")
    elif e.error_code == "SERVICE_OVERLOADED":
        print("Server is busy, try again in a few minutes")
```
### JavaScript - Error Handling

```javascript
class ChatterboxError extends Error {
    constructor(statusCode, errorCode, message, detail) {
        super(message);
        this.name = 'ChatterboxError';
        this.statusCode = statusCode;
        this.errorCode = errorCode;
        this.detail = detail;
    }
}

class ChatterboxClient {
    constructor(baseUrl = 'http://localhost:7860') {
        this.baseUrl = baseUrl;
    }
    
    async handleResponse(response) {
        if (response.ok) {
            return response;
        }
        
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = {
                error_code: `HTTP_${response.status}`,
                error_message: response.statusText || 'Unknown error',
                detail: null
            };
        }
        
        throw new ChatterboxError(
            response.status,
            errorData.error_code,
            errorData.error_message,
            errorData.detail
        );
    }
    
    async generateTTS(text, options = {}) {
        const payload = { text, ...options };
        
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            return await this.handleResponse(response);
            
        } catch (error) {
            if (error instanceof ChatterboxError) {
                throw error;
            }
            
            // Network or other errors
            throw new ChatterboxError(
                0,
                'NETWORK_ERROR',
                'Failed to connect to server',
                error.message
            );
        }
    }
}
```
## Troubleshooting Common Issues

### 1. Voice File Not Found
**Error**: `RESOURCE_NOT_FOUND` or `VOICE_NOT_FOUND`

**Solutions**:
```bash
# Check if file exists
ls reference_audio/speaker1.wav

# List available voices
curl http://localhost:7860/api/v1/voices

# Check file permissions (Linux/Mac)
ls -la reference_audio/

# Upload missing voice
curl -X POST http://localhost:7860/api/v1/voice \
  -F "audio_file=@speaker1.wav" \
  -F "metadata={\"name\":\"Speaker 1\"}"
```

### 2. Invalid Parameters
**Error**: `INVALID_PARAMETERS`

**Common Parameter Issues**:
```python
# ❌ Invalid temperature
{"text": "Hello", "temperature": 2.0}  # Max is 1.5

# ✅ Correct temperature
{"text": "Hello", "temperature": 0.8}

# ❌ Invalid export format
{"text": "Hello", "export_formats": ["avi"]}

# ✅ Valid export formats
{"text": "Hello", "export_formats": ["wav", "mp3", "flac"]}

# ❌ Empty text
{"text": ""}

# ✅ Non-empty text
{"text": "Hello world"}
```

### 3. File Upload Issues
**Error**: `UNSUPPORTED_FORMAT` or `FILE_TOO_LARGE`

**Solutions**:
```bash
# Check file format
file my_audio.wav

# Convert unsupported format
ffmpeg -i input.m4a -ar 22050 -ac 1 output.wav

# Reduce file size
ffmpeg -i large_file.wav -b:a 128k compressed.mp3

# Check file size
ls -lh my_audio.wav
```
### 4. Service Unavailable
**Error**: `SERVICE_OVERLOADED` or `MODEL_LOADING_FAILED`

**Solutions**:
```python
# Implement retry with backoff
import time
import random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except ChatterboxAPIError as e:
            if e.error_code in ['SERVICE_OVERLOADED', 'MODEL_LOADING_FAILED']:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retry {attempt + 1} after {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
            raise

# Check server health
response = requests.get("http://localhost:7860/api/v1/health")
print(f"Server status: {response.json()}")
```

### 5. Network and Connection Issues

**Connection Errors**:
```python
# Test basic connectivity
import requests

try:
    response = requests.get("http://localhost:7860/api/v1/health", timeout=5)
    print(f"Server reachable: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to server - check if it's running")
except requests.exceptions.Timeout:
    print("Server response timeout - may be overloaded")

# Configure timeouts appropriately
response = requests.post(
    url,
    json=data,
    timeout=(10, 300)  # (connect_timeout, read_timeout)
)
```

## Error Prevention Best Practices

### 1. Input Validation
```python
def validate_tts_request(text, reference_audio=None, **kwargs):
    """Validate TTS request before sending"""
    
    errors = []
    
    # Text validation
    if not text or not text.strip():
        errors.append("Text cannot be empty")
    if len(text) > 10000:  # Reasonable limit
        errors.append("Text too long (max 10,000 characters)")
    
    # Parameter validation
    temp = kwargs.get('temperature', 0.7)
    if not 0.1 <= temp <= 1.5:
        errors.append(f"Temperature {temp} out of range (0.1-1.5)")
    
    # Format validation
    formats = kwargs.get('export_formats', ['wav'])
    valid_formats = {'wav', 'mp3', 'flac'}
    invalid_formats = set(formats) - valid_formats
    if invalid_formats:
        errors.append(f"Invalid formats: {invalid_formats}")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return True
```
### 2. File Existence Checks
```python
def check_voice_availability(voice_filename, base_url="http://localhost:7860"):
    """Check if voice file exists before using"""
    
    try:
        response = requests.get(f"{base_url}/api/v1/voices")
        if response.status_code == 200:
            voices = response.json()
            available_voices = [v['filename'] for v in voices.get('voices', [])]
            
            if voice_filename not in available_voices:
                print(f"Voice '{voice_filename}' not found.")
                print(f"Available voices: {', '.join(available_voices[:5])}")
                return False
            return True
    except Exception as e:
        print(f"Could not check voice availability: {e}")
        return False

# Usage
if check_voice_availability("speaker1.wav"):
    # Proceed with TTS request
    response = generate_tts("Hello", reference_audio="speaker1.wav")
```

### 3. Progressive Error Recovery
```python
def robust_tts_generation(text, preferred_voice=None, fallback_voices=None):
    """Try multiple voices with fallback options"""
    
    voices_to_try = []
    if preferred_voice:
        voices_to_try.append(preferred_voice)
    if fallback_voices:
        voices_to_try.extend(fallback_voices)
    voices_to_try.append(None)  # No reference audio fallback
    
    for voice in voices_to_try:
        try:
            if voice:
                print(f"Trying voice: {voice}")
            else:
                print("Trying without reference audio")
                
            response = generate_tts(text, reference_audio=voice)
            print(f"✓ Success with voice: {voice or 'default'}")
            return response
            
        except ChatterboxAPIError as e:
            if e.error_code == "RESOURCE_NOT_FOUND":
                print(f"✗ Voice '{voice}' not found, trying next...")
                continue
            else:
                # Other errors should not be retried
                raise
    
    raise Exception("All voice options failed")

# Usage
response = robust_tts_generation(
    "Hello world",
    preferred_voice="speaker1.wav",
    fallback_voices=["narrator.wav", "default.wav"]
)
```

## Monitoring and Logging

### Request ID Tracking
```python
import uuid

def make_tracked_request(url, data):
    """Make request with unique tracking ID"""
    
    request_id = str(uuid.uuid4())
    headers = {'X-Request-ID': request_id}
    
    print(f"Making request {request_id}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Request {request_id} completed: {response.status_code}")
        return response
    except Exception as e:
        print(f"Request {request_id} failed: {e}")
        raise
```

### Error Analytics
```python
import logging
from collections import defaultdict

class ErrorTracker:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.logger = logging.getLogger(__name__)
    
    def track_error(self, error_code, endpoint):
        self.error_counts[(endpoint, error_code)] += 1
        self.logger.error(f"{endpoint}: {error_code}")
    
    def get_error_summary(self):
        return dict(self.error_counts)

# Usage
error_tracker = ErrorTracker()

try:
    response = generate_tts("Hello")
except ChatterboxAPIError as e:
    error_tracker.track_error(e.error_code, "/api/v1/tts")
    raise
```

## See Also

- [Streaming Responses Guide](streaming-responses.md) - Response handling
- [File Uploads Guide](file-uploads.md) - Upload error handling  
- [TTS Endpoint](../endpoints/tts.md) - TTS-specific errors
- [Voice Conversion Endpoint](../endpoints/voice-conversion.md) - VC-specific errors
- [Health Endpoint](../endpoints/health.md) - System status checking

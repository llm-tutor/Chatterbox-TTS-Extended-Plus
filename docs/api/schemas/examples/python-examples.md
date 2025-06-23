# Python Examples
## Chatterbox TTS Extended Plus API Client

> **Requirements**: `pip install requests`
> **Base URL**: `http://localhost:7860`

---

## Basic Setup

### Import and Configuration
```python
import requests
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# API Configuration
API_BASE = "http://localhost:7860"
API_TIMEOUT = 300  # 5 minutes for generation requests

class ChatterboxClient:
    def __init__(self, base_url: str = API_BASE, timeout: int = API_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise
```

---

## Health Check

### Simple Health Check
```python
def check_health() -> Dict[str, Any]:
    """Check API health status."""
    response = requests.get(f"{API_BASE}/api/v1/health")
    return response.json()

# Usage
try:
    health = check_health()
    print(f"API Status: {health['status']}")
    print(f"Uptime: {health['uptime']}")
except Exception as e:
    print(f"Health check failed: {e}")
```

### Advanced Health Check with Client
```python
client = ChatterboxClient()

def check_api_health(client: ChatterboxClient) -> bool:
    """Check if API is healthy and ready."""
    try:
        response = client._make_request("GET", "/api/v1/health")
        data = response.json()
        return data.get("status") == "healthy"
    except Exception as e:
        print(f"API health check failed: {e}")
        return False

# Usage
if check_api_health(client):
    print("✅ API is healthy and ready")
else:
    print("❌ API is not responding")
```

---

## Text-to-Speech (TTS)

### Basic TTS Generation
```python
def generate_tts_basic(text: str, output_path: str = "speech.wav") -> bool:
    """Generate basic TTS without voice cloning."""
    payload = {
        "text": text,
        "export_formats": ["wav"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/tts",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ TTS generated: {output_path}")
        return True
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        return False

# Usage
generate_tts_basic("Hello, this is a test of the TTS API.")
```

### TTS with Voice Cloning
```python
def generate_tts_with_voice(
    text: str,
    reference_voice: str,
    output_path: str = "cloned_speech.wav",
    **kwargs
) -> bool:
    """Generate TTS with voice cloning."""
    payload = {
        "text": text,
        "reference_audio_filename": reference_voice,
        "export_formats": ["wav", "mp3"],
        **kwargs  # Additional parameters
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/tts",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Voice cloned TTS generated: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Voice cloning failed: {e}")
        return False

# Usage
generate_tts_with_voice(
    text="This will sound like the reference speaker.",
    reference_voice="speaker1/formal.wav",
    exaggeration=0.7,
    temperature=0.8,
    seed=42
)
```

### Advanced TTS with Full Control
```python
class TTSGenerator:
    def __init__(self, client: ChatterboxClient):
        self.client = client
    
    def generate(
        self,
        text: str,
        reference_audio_filename: Optional[str] = None,
        exaggeration: float = 0.5,
        temperature: float = 0.75,
        seed: int = 0,
        speed_factor: float = 1.0,
        speed_factor_library: str = "auto",
        export_formats: List[str] = None,
        output_path: Optional[str] = None,
        get_metadata: bool = False
    ) -> Dict[str, Any]:
        """Generate TTS with advanced parameters."""
        
        if export_formats is None:
            export_formats = ["wav"]
        
        payload = {
            "text": text,
            "exaggeration": exaggeration,
            "temperature": temperature,
            "seed": seed,
            "speed_factor": speed_factor,
            "speed_factor_library": speed_factor_library,
            "export_formats": export_formats,
            "disable_watermark": True
        }
        
        if reference_audio_filename:
            payload["reference_audio_filename"] = reference_audio_filename
        
        try:
            if get_metadata:
                # Get JSON response with metadata
                response = self.client._make_request(
                    "POST", 
                    "/api/v1/tts?response_mode=url", 
                    json=payload
                )
                return response.json()
            else:
                # Stream audio directly
                response = self.client._make_request(
                    "POST", 
                    "/api/v1/tts", 
                    json=payload, 
                    stream=True
                )
                
                if output_path:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"✅ Advanced TTS saved: {output_path}")
                
                return {"success": True, "file_path": output_path}
                
        except Exception as e:
            print(f"❌ Advanced TTS failed: {e}")
            return {"success": False, "error": str(e)}

# Usage
client = ChatterboxClient()
tts = TTSGenerator(client)

result = tts.generate(
    text="This is advanced TTS with speed control and high quality.",
    reference_audio_filename="speaker2/energetic.wav",
    speed_factor=1.2,
    speed_factor_library="audiostretchy",
    temperature=0.8,
    exaggeration=0.6,
    seed=42,
    output_path="advanced_speech.wav"
)
```

---

## Voice Conversion (VC)

### Basic Voice Conversion
```python
def convert_voice_basic(
    input_file: str,
    target_voice: str,
    output_path: str = "converted_voice.wav"
) -> bool:
    """Basic voice conversion with local files."""
    payload = {
        "input_audio_source": input_file,
        "target_voice_source": target_voice,
        "export_formats": ["wav"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/vc",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Voice conversion completed: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Voice conversion failed: {e}")
        return False

# Usage
convert_voice_basic(
    input_file="my_recording.wav",
    target_voice="celebrity_voices/actor1.wav"
)
```

### Voice Conversion with File Upload
```python
def convert_voice_upload(
    input_file_path: str,
    target_voice: str,
    output_path: str = "uploaded_conversion.wav",
    chunk_sec: int = 30
) -> bool:
    """Convert voice with direct file upload."""
    
    try:
        with open(input_file_path, 'rb') as audio_file:
            files = {
                'input_audio': audio_file,
            }
            data = {
                'target_voice_source': target_voice,
                'chunk_sec': chunk_sec,
                'export_formats': 'wav,mp3'
            }
            
            response = requests.post(
                f"{API_BASE}/api/v1/vc",
                files=files,
                data=data,
                stream=True
            )
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Upload conversion completed: {output_path}")
            return True
    except Exception as e:
        print(f"❌ Upload conversion failed: {e}")
        return False

# Usage
convert_voice_upload(
    input_file_path="./local_audio.wav",
    target_voice="speaker1.wav",
    chunk_sec=45
)
```

---

## Voice Management

### List and Search Voices
```python
def list_voices(search: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """List available voices with optional search."""
    params = {"page": page, "page_size": page_size}
    if search:
        params["search"] = search
    
    try:
        response = requests.get(f"{API_BASE}/api/v1/voices", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to list voices: {e}")
        return {"voices": [], "total": 0}

# Usage
voices = list_voices(search="professional")
print(f"Found {voices['total']} voices:")
for voice in voices['voices']:
    print(f"  - {voice['filename']}: {voice['name']}")
```

### Upload New Voice
```python
def upload_voice(
    voice_file_path: str,
    name: str,
    description: str = "",
    tags: List[str] = None,
    folder_path: str = ""
) -> bool:
    """Upload a new voice file."""
    
    try:
        with open(voice_file_path, 'rb') as voice_file:
            files = {'voice_file': voice_file}
            data = {
                'name': name,
                'description': description,
                'tags': ','.join(tags) if tags else '',
                'folder_path': folder_path
            }
            
            response = requests.post(
                f"{API_BASE}/api/v1/voice",
                files=files,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Voice uploaded: {result['filename']}")
            return True
    except Exception as e:
        print(f"❌ Voice upload failed: {e}")
        return False

# Usage
upload_voice(
    voice_file_path="./my_custom_voice.wav",
    name="My Custom Speaker",
    description="High-quality recording for demonstrations",
    tags=["custom", "demo", "clear"],
    folder_path="custom_voices"
)
```

---

## File Operations

### List Generated Files
```python
def list_generated_files(limit: int = 50) -> List[Dict[str, Any]]:
    """List recently generated files."""
    try:
        response = requests.get(f"{API_BASE}/api/v1/outputs", params={"limit": limit})
        response.raise_for_status()
        return response.json().get("files", [])
    except Exception as e:
        print(f"❌ Failed to list files: {e}")
        return []

# Usage
files = list_generated_files()
for file in files[:5]:  # Show last 5 files
    print(f"📁 {file['filename']} ({file['size_mb']:.1f}MB) - {file['created']}")
```

### Download Generated Files
```python
def download_generated_file(filename: str, output_path: Optional[str] = None) -> bool:
    """Download a generated file by filename."""
    if not output_path:
        output_path = filename
    
    try:
        response = requests.get(f"{API_BASE}/outputs/{filename}", stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded: {filename} -> {output_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

# Usage
download_generated_file("tts_2025-06-22_143022_456_temp0.75_seed42.wav")
```

---

## Complete Workflow Examples

### Text-to-Speech Workflow
```python
def complete_tts_workflow():
    """Complete TTS workflow from text to audio file."""
    client = ChatterboxClient()
    tts = TTSGenerator(client)
    
    # Check API health
    if not check_api_health(client):
        print("❌ API not available")
        return
    
    # List available voices
    voices = list_voices(search="professional")
    if not voices['voices']:
        print("❌ No professional voices found")
        return
    
    reference_voice = voices['voices'][0]['filename']
    print(f"📢 Using voice: {reference_voice}")
    
    # Generate TTS
    text = "Welcome to our professional presentation."
    
    result = tts.generate(
        text=text,
        reference_audio_filename=reference_voice,
        temperature=0.8,
        exaggeration=0.6,
        speed_factor=1.1,
        output_path="professional_speech.wav"
    )
    
    if result['success']:
        print("✅ TTS workflow completed successfully!")
    else:
        print(f"❌ TTS workflow failed: {result.get('error')}")

# Run workflow
complete_tts_workflow()
```

---

## Error Handling and Retry Logic

### Robust Request Handler
```python
import time
from typing import Callable, Any

def retry_request(
    func: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
) -> Any:
    """Retry a request function with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff ** attempt)
            print(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

# Usage with TTS
def reliable_tts_generation(text: str, **kwargs) -> bool:
    """Generate TTS with automatic retry on failure."""
    
    def tts_request():
        payload = {"text": text, **kwargs}
        response = requests.post(f"{API_BASE}/api/v1/tts", json=payload, stream=True)
        response.raise_for_status()
        return response
    
    try:
        response = retry_request(tts_request)
        
        with open("reliable_speech.wav", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ Reliable TTS generation completed")
        return True
    except Exception as e:
        print(f"❌ All retry attempts failed: {e}")
        return False

# Usage
reliable_tts_generation(
    text="This request will retry automatically on failure.",
    export_formats=["wav"]
)
```

---

## Configuration and Best Practices

### Client Configuration
```python
import logging
from dataclasses import dataclass

@dataclass
class ClientConfig:
    """Configuration for Chatterbox API client."""
    base_url: str = "http://localhost:7860"
    timeout: int = 300
    max_retries: int = 3
    chunk_size: int = 8192
    enable_logging: bool = True

# Usage
config = ClientConfig(timeout=600, max_retries=5)
client = ChatterboxClient(config.base_url)
```

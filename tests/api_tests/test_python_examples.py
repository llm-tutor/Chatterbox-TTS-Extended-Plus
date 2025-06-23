#!/usr/bin/env python3
"""
Test Python Examples from API Documentation
Validates all Python code examples work as expected
"""

import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import our test runner
from test_runner import APITester, API_BASE, NORMAL_TIMEOUT

# Copy the ChatterboxClient class from our examples
class ChatterboxClient:
    def __init__(self, base_url: str = API_BASE, timeout: int = NORMAL_TIMEOUT):
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

class PythonExamplesTester:
    def __init__(self, api_tester: APITester):
        self.tester = api_tester
        self.test_files_dir = Path(__file__).parent / "temp_files"
        self.test_files_dir.mkdir(exist_ok=True)
        self.client = ChatterboxClient()
    
    def test_health_check_basic(self, result):
        """Test basic health check function."""
        def check_health() -> Dict[str, Any]:
            response = requests.get(f"{API_BASE}/api/v1/health")
            return response.json()
        
        health = check_health()
        if health.get("status") != "healthy":
            raise Exception(f"API not healthy: {health}")
        
        result.notes.append(f"Server status: {health.get('status')}")
        result.notes.append(f"Uptime: {health.get('uptime', 'unknown')}")
    
    def test_health_check_with_client(self, result):
        """Test health check with ChatterboxClient."""
        def check_api_health(client: ChatterboxClient) -> bool:
            try:
                response = client._make_request("GET", "/api/v1/health")
                data = response.json()
                return data.get("status") == "healthy"
            except Exception as e:
                print(f"API health check failed: {e}")
                return False
        
        if not check_api_health(self.client):
            raise Exception("Health check with client failed")
        
        result.notes.append("ChatterboxClient health check passed")
    
    def test_basic_tts_generation(self, result):
        """Test basic TTS generation function."""
        def generate_tts_basic(text: str, output_path: str = "speech.wav") -> bool:
            payload = {
                "text": text,
                "export_formats": ["wav"]
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/api/v1/tts",
                    json=payload,
                    stream=True,
                    timeout=45  # Extended timeout for generation
                )
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return True
            except Exception as e:
                print(f"TTS generation failed: {e}")
                return False
        
        output_file = self.test_files_dir / "python_basic_tts.wav"
        success = generate_tts_basic("Python TTS test", str(output_file))
        
        if not success:
            raise Exception("Basic TTS generation failed")
        
        if not output_file.exists():
            raise Exception("TTS output file was not created")
        
        file_size = output_file.stat().st_size
        if file_size < 1000:
            raise Exception(f"TTS output file too small: {file_size} bytes")
        
        result.notes.append(f"Generated TTS file: {file_size} bytes")
        
        # Clean up
        output_file.unlink()
    
    def test_list_voices(self, result):
        """Test voice listing function."""
        def list_voices(search: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
            params = {"page": page, "page_size": page_size}
            if search:
                params["search"] = search
            
            try:
                response = requests.get(f"{API_BASE}/api/v1/voices", params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Failed to list voices: {e}")
                return {"voices": [], "total": 0}
        
        voices = list_voices()
        if "voices" not in voices:
            raise Exception("No voices field in response")
        
        voice_count = voices.get("total", len(voices["voices"]))
        result.notes.append(f"Found {voice_count} voices")
        
        # Test search functionality if voices exist
        if voice_count > 0:
            search_result = list_voices(search="test")
            result.notes.append(f"Search test returned {len(search_result.get('voices', []))} results")
    
    def test_list_generated_files(self, result):
        """Test listing generated files function."""
        def list_generated_files(limit: int = 50) -> List[Dict[str, Any]]:
            try:
                response = requests.get(f"{API_BASE}/api/v1/outputs", params={"limit": limit})
                response.raise_for_status()
                return response.json().get("files", [])
            except Exception as e:
                print(f"Failed to list files: {e}")
                return []
        
        files = list_generated_files()
        if not isinstance(files, list):
            raise Exception("Expected list of files")
        
        file_count = len(files)
        result.notes.append(f"Found {file_count} generated files")
    
    def test_tts_with_voice_cloning(self, result):
        """Test TTS with voice cloning if voices are available."""
        # First get available voices
        response = requests.get(f"{API_BASE}/api/v1/voices")
        voices_data = response.json()
        
        if not voices_data.get("voices"):
            result.notes.append("Skipped: No voices available for cloning test")
            return
        
        # Use the first available voice
        first_voice = voices_data["voices"][0]
        if "filename" not in first_voice:
            result.notes.append("Skipped: Voice data missing filename field")
            return
            
        reference_voice = first_voice["filename"]
        
        def generate_tts_with_voice(
            text: str,
            reference_voice: str,
            output_path: str = "cloned_speech.wav",
            **kwargs
        ) -> bool:
            payload = {
                "text": text,
                "reference_audio_filename": reference_voice,
                "export_formats": ["wav"],
                **kwargs
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/api/v1/tts",
                    json=payload,
                    stream=True,
                    timeout=60  # Extended timeout for voice cloning
                )
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return True
            except Exception as e:
                print(f"Voice cloning failed: {e}")
                return False
        
        output_file = self.test_files_dir / "python_voice_cloned.wav"
        success = generate_tts_with_voice(
            "Voice cloning test with Python",
            reference_voice,
            str(output_file),
            exaggeration=0.7,
            temperature=0.8
        )
        
        if not success:
            raise Exception("Voice cloning TTS failed")
        
        if not output_file.exists():
            raise Exception("Voice cloned TTS output file was not created")
        
        file_size = output_file.stat().st_size
        result.notes.append(f"Voice cloned TTS: {file_size} bytes using {reference_voice}")
        
        # Clean up
        output_file.unlink()


def run_python_tests(api_tester: APITester):
    """Run all Python example tests."""
    python_tester = PythonExamplesTester(api_tester)
    
    # Basic health checks
    api_tester.run_test("Python: Basic Health Check", python_tester.test_health_check_basic)
    api_tester.run_test("Python: Client Health Check", python_tester.test_health_check_with_client)
    
    # TTS tests
    api_tester.run_test("Python: Basic TTS Generation", python_tester.test_basic_tts_generation)
    api_tester.run_test("Python: TTS with Voice Cloning", python_tester.test_tts_with_voice_cloning)
    
    # API listing tests
    api_tester.run_test("Python: List Voices", python_tester.test_list_voices)
    api_tester.run_test("Python: List Generated Files", python_tester.test_list_generated_files)

if __name__ == "__main__":
    from test_runner import APITester
    
    tester = APITester()
    if tester.warm_up_server():
        run_python_tests(tester)
        tester.generate_report()

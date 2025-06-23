#!/usr/bin/env python3
"""
Test cURL Examples from API Documentation
Validates all cURL commands work as expected
"""

import subprocess
import json
import time
import requests
from pathlib import Path
from test_runner import APITester, API_BASE

class CurlExamplesTester:
    def __init__(self, api_tester: APITester):
        self.tester = api_tester
        self.test_files_dir = Path(__file__).parent / "temp_files"
        self.test_files_dir.mkdir(exist_ok=True)
    
    def run_curl_command(self, cmd: str, timeout: int = 30) -> dict:
        """Run a curl command and return parsed result."""
        try:
            # Replace localhost with full URL if needed
            if "localhost:7860" not in cmd:
                cmd = cmd.replace("http://localhost:7860", API_BASE)
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_health_check(self, result):
        """Test basic health check cURL command."""
        cmd = f'curl -s {API_BASE}/api/v1/health'
        curl_result = self.run_curl_command(cmd)
        
        if not curl_result["success"]:
            raise Exception(f"Health check curl failed: {curl_result['stderr']}")
        
        try:
            health_data = json.loads(curl_result["stdout"])
            if health_data.get("status") != "healthy":
                raise Exception(f"API not healthy: {health_data}")
            result.notes.append(f"Server uptime: {health_data.get('uptime', 'unknown')}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {curl_result['stdout']}")
    
    def test_basic_tts_curl(self, result):
        """Test basic TTS generation with cURL."""
        output_file = self.test_files_dir / "curl_tts_basic.wav"
        
        # Use PowerShell-compatible curl syntax
        cmd = f'''curl -s -X POST {API_BASE}/api/v1/tts -H "Content-Type: application/json" -d "{{\\"text\\": \\"Hello from cURL test\\", \\"export_formats\\": [\\"wav\\"]}}" --output "{output_file}"'''
        
        curl_result = self.run_curl_command(cmd, timeout=45)
        
        if not curl_result["success"]:
            raise Exception(f"TTS curl failed: stdout='{curl_result['stdout']}' stderr='{curl_result['stderr']}' returncode={curl_result['returncode']}")
        
        if not output_file.exists():
            raise Exception("TTS output file was not created")
        
        file_size = output_file.stat().st_size
        if file_size < 1000:  # Expect at least 1KB for audio
            raise Exception(f"TTS output file too small: {file_size} bytes")
        
        result.notes.append(f"Generated TTS file: {file_size} bytes")
        
        # Clean up
        output_file.unlink()
    
    def test_tts_json_response_curl(self, result):
        """Test TTS with JSON response (legacy mode) - using requests since cURL syntax is complex in PowerShell."""
        # Use requests directly to avoid PowerShell cURL issues
        payload = {
            "text": "JSON response test", 
            "export_formats": ["wav"]
        }
        params = {"response_mode": "url"}
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/tts",
                params=params,
                json=payload,
                timeout=45
            )
            response.raise_for_status()
            
            response_data = response.json()
            if not response_data.get("success", True):
                raise Exception(f"TTS generation failed: {response_data}")
            
            # Check for output_files field (correct field name)
            if "output_files" not in response_data or not response_data["output_files"]:
                raise Exception("No output_files in TTS response")
            
            file_formats = [f['format'] for f in response_data["output_files"]]
            result.notes.append(f"Generated files: {file_formats}")
            result.notes.append("Used requests instead of cURL due to PowerShell syntax complexity")
            
        except Exception as e:
            raise Exception(f"TTS JSON response test failed: {e}")
    
    def test_voices_list_curl(self, result):
        """Test listing voices with cURL."""
        cmd = f'curl -s {API_BASE}/api/v1/voices'
        curl_result = self.run_curl_command(cmd)
        
        if not curl_result["success"]:
            raise Exception(f"Voices list curl failed: {curl_result['stderr']}")
        
        try:
            voices_data = json.loads(curl_result["stdout"])
            if "voices" not in voices_data:
                raise Exception("No voices field in response")
            
            voice_count = len(voices_data["voices"])
            result.notes.append(f"Found {voice_count} voices")
            
            # Test voice search if voices exist
            if voice_count > 0:
                search_cmd = f'curl -s "{API_BASE}/api/v1/voices?search=test"'
                search_result = self.run_curl_command(search_cmd)
                if search_result["success"]:
                    search_data = json.loads(search_result["stdout"])
                    result.notes.append(f"Search test returned {len(search_data.get('voices', []))} results")
            
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {curl_result['stdout']}")
    
    def test_outputs_list_curl(self, result):
        """Test listing generated files with cURL."""
        cmd = f'curl -s {API_BASE}/api/v1/outputs'
        curl_result = self.run_curl_command(cmd)
        
        if not curl_result["success"]:
            raise Exception(f"Outputs list curl failed: {curl_result['stderr']}")
        
        try:
            outputs_data = json.loads(curl_result["stdout"])
            if "files" not in outputs_data:
                raise Exception("No files field in outputs response")
            
            file_count = len(outputs_data["files"])
            result.notes.append(f"Found {file_count} output files")
            
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {curl_result['stdout']}")

def run_curl_tests(api_tester: APITester):
    """Run all cURL example tests."""
    curl_tester = CurlExamplesTester(api_tester)
    
    # Health check
    api_tester.run_test("cURL: Health Check", curl_tester.test_health_check)
    
    # Basic TTS
    api_tester.run_test("cURL: Basic TTS Generation", curl_tester.test_basic_tts_curl)
    
    # TTS JSON response
    api_tester.run_test("cURL: TTS JSON Response", curl_tester.test_tts_json_response_curl)
    
    # Voice listing
    api_tester.run_test("cURL: List Voices", curl_tester.test_voices_list_curl)
    
    # Output listing
    api_tester.run_test("cURL: List Outputs", curl_tester.test_outputs_list_curl)

if __name__ == "__main__":
    from test_runner import APITester
    
    tester = APITester()
    if tester.warm_up_server():
        run_curl_tests(tester)
        tester.generate_report()

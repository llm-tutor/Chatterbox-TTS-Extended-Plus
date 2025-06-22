#!/usr/bin/env python3
"""
Test suite for Phase 10 Task 10.3: Voice Upload Endpoint
Tests the voice upload functionality including file validation, metadata creation, and API endpoint.
"""

import requests
import json
import tempfile
from pathlib import Path
import time

# API Configuration
API_BASE_URL = "http://127.0.0.1:7860"
TEST_TIMEOUT = 30

def test_voice_upload_functionality():
    """Test the voice upload endpoint functionality"""
    print("=== Testing Phase 10 Task 10.3: Voice Upload Endpoint ===")
    
    # Test 1: Basic voice upload
    print("\n1. Testing basic voice upload...")
    
    # Create a test audio file (simulate with empty content for API testing)
    test_filename = f"test_voice_{int(time.time())}.wav"
    
    # For this test, we'll create minimal WAV file content
    # WAV header for a minimal valid file
    wav_header = b'RIFF\x2c\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    try:
        # Test basic upload
        files = {'voice_file': (test_filename, wav_header, 'audio/wav')}
        data = {
            'name': 'Test Voice Upload',
            'description': 'A test voice for upload functionality',
            'tags': 'test,upload,automation',
            'folder_path': 'test_uploads'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/voice",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Voice uploaded - {result['filename']}")
            print(f"   Message: {result['message']}")
            print(f"   Metadata: Name='{result['voice_metadata']['name']}', Tags={result['voice_metadata']['tags']}")
        else:
            print(f"   FAILED: Upload failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Upload with default parameters
    print("\n2. Testing upload with default parameters...")
    
    try:
        test_filename_2 = f"test_voice_params_{int(time.time())}.wav"
        default_params = {
            'temperature': 0.8,
            'exaggeration': 0.6,
            'cfg_weight': 1.2
        }
        
        files = {'voice_file': (test_filename_2, wav_header, 'audio/wav')}
        data = {
            'name': 'Test Voice with Parameters',
            'description': 'Voice with default TTS parameters',
            'default_parameters': json.dumps(default_params),
            'overwrite': False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/voice",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Voice with parameters uploaded - {result['filename']}")
            print(f"   Default parameters: {result['voice_metadata']['default_parameters']}")
        else:
            print(f"   FAILED: Upload with parameters failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Invalid file format (should fail)
    print("\n3. Testing invalid file format (should fail)...")
    
    try:
        invalid_content = b'This is not an audio file'
        files = {'voice_file': ('test_invalid.txt', invalid_content, 'text/plain')}
        data = {'name': 'Invalid File Test'}
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/voice",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 400:
            print(f"   SUCCESS: Invalid file correctly rejected")
            print(f"   Error message: {response.json().get('detail', 'No detail')}")
        else:
            print(f"   UNEXPECTED: Invalid file not rejected (status {response.status_code})")
            
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n=== Phase 10 Task 10.3 Voice Upload Tests Complete ===")


if __name__ == "__main__":
    test_voice_upload_functionality()

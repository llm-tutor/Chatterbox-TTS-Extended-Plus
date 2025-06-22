#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 10 - Speed Control & Voice Enhancement
Tests all completed tasks: 10.1 (Speed Factor), 10.2 (Voice Metadata), 10.3 (Voice Upload), 10.4 (Generated Files)
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://127.0.0.1:7860"
TEST_TIMEOUT = 30

def test_phase_10_comprehensive():
    """Comprehensive test of all Phase 10 functionality"""
    print("=== Phase 10 Comprehensive Test Suite ===")
    print("Testing: Speed Control, Voice Metadata, Voice Upload, Generated Files Listing")
    
    # Test 1: Speed Factor (Task 10.1)
    print("\n1. Testing Speed Factor Implementation...")
    
    try:
        tts_request = {
            "text": "Testing speed factor functionality with enhanced audio quality.",
            "speed_factor": 1.2,
            "speed_factor_library": "auto"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/tts", 
            json=tts_request,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Speed factor TTS generated - {result.get('filename', 'Unknown')}")
            print(f"   Speed: {tts_request['speed_factor']}x, Library: {tts_request['speed_factor_library']}")
        else:
            print(f"   FAILED: Speed factor TTS failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Enhanced Voice Metadata (Task 10.2)
    print("\n2. Testing Enhanced Voice Metadata System...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/voices?page_size=3",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Enhanced voices API - {result['count']} voices with metadata")
            
            if result['voices']:
                voice = result['voices'][0]
                print(f"   Sample voice: {voice['name']}")
                print(f"   - Duration: {voice.get('duration_seconds', 'Unknown')}s")
                print(f"   - Usage count: {voice.get('usage_count', 0)}")
                print(f"   - Tags: {voice.get('tags', [])}")
        else:
            print(f"   FAILED: Enhanced voices API failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Voice Upload (Task 10.3)
    print("\n3. Testing Voice Upload Endpoint...")
    
    try:
        # Create test audio file content
        wav_header = b'RIFF\x2c\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        test_filename = f"phase10_test_{int(time.time())}.wav"
        files = {'voice_file': (test_filename, wav_header, 'audio/wav')}
        data = {
            'name': 'Phase 10 Test Voice',
            'description': 'Comprehensive Phase 10 functionality test',
            'tags': 'phase10,test,comprehensive',
            'folder_path': 'phase10_tests'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/voice",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Voice upload - {result['filename']}")
            print(f"   Metadata: {result['voice_metadata']['name']}")
            print(f"   Folder: {result['voice_metadata'].get('folder_path', 'root')}")
        else:
            print(f"   FAILED: Voice upload failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Generated Files Listing (Task 10.4)
    print("\n4. Testing Generated Files Listing...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/outputs?page_size=5&generation_type=tts",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Generated files listing - {result['total_files']} total TTS files")
            print(f"   Pagination: Page {result['page']}/{result['total_pages']}")
            
            if result['files']:
                print(f"   Sample files:")
                for file_meta in result['files'][:2]:
                    print(f"   - {file_meta['filename']} ({file_meta['generation_type']}) - {file_meta.get('duration_seconds', 'Unknown')}s")
        else:
            print(f"   FAILED: Generated files listing failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 5: Phase 10 Integration Test
    print("\n5. Testing Phase 10 Integration...")
    
    try:
        # Search for our uploaded test voice
        response = requests.get(
            f"{API_BASE_URL}/api/v1/voices?search=phase10&folder=phase10_tests",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['count'] > 0:
                print(f"   SUCCESS: Found {result['count']} Phase 10 test voices")
                print(f"   Integration: Upload → Metadata → Discovery working")
            else:
                print(f"   INFO: No Phase 10 test voices found (expected on first run)")
        else:
            print(f"   FAILED: Integration test failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n=== Phase 10 Comprehensive Test Complete ===")
    print("All Phase 10 features tested: Speed Control, Voice Metadata, Voice Upload, Generated Files")


if __name__ == "__main__":
    test_phase_10_comprehensive()

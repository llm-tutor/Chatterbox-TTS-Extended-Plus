#!/usr/bin/env python3
"""
Enhanced test suite for Phase 10 Task 10.3: Complete Voice Management
Tests voice upload, metadata updates, deletion, and folder structure management.
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://127.0.0.1:7860"
TEST_TIMEOUT = 30

def test_enhanced_voice_management():
    """Test enhanced voice management functionality"""
    print("=== Testing Enhanced Phase 10 Task 10.3: Complete Voice Management ===")
    
    # Test data
    test_timestamp = int(time.time())
    test_voice_name = f"enhanced_test_{test_timestamp}"
    test_filename = f"{test_voice_name}.wav"
    
    # WAV file content for testing
    wav_header = b'RIFF\x2c\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    # Test 1: Voice Upload (existing functionality)
    print("\n1. Testing voice upload...")
    
    try:
        files = {'voice_file': (test_filename, wav_header, 'audio/wav')}
        data = {
            'name': test_voice_name,
            'description': 'Test voice for enhanced management',
            'tags': 'test,enhanced,management',
            'folder_path': 'test_enhanced'
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
            uploaded_filename = result['filename']
        else:
            print(f"   FAILED: Voice upload failed with status {response.status_code}")
            return  # Can't continue without uploaded voice
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # Test 2: Metadata Update
    print("\n2. Testing metadata update...")
    
    try:
        metadata_update = {
            'description': 'Updated description for enhanced test',
            'tags': ['test', 'enhanced', 'updated'],
            'default_parameters': {'temperature': 0.9, 'exaggeration': 0.7}
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/voice/{uploaded_filename}/metadata",
            json=metadata_update,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Metadata updated")
            print(f"   New description: {result['voice_metadata']['description']}")
            print(f"   New tags: {result['voice_metadata']['tags']}")
        else:
            print(f"   FAILED: Metadata update failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Folder Structure
    print("\n3. Testing folder structure API...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/voices/folders",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Found {result['total_folders']} folders with {result['total_voices']} total voices")
            
            # Look for our test folder
            test_folder_found = False
            for folder in result['folders']:
                if folder['path'] == 'test_enhanced':
                    print(f"   Test folder found: {folder['voice_count']} voices")
                    test_folder_found = True
                    break
            
            if not test_folder_found:
                print(f"   WARNING: Test folder 'test_enhanced' not found")
                
        else:
            print(f"   FAILED: Folder structure failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Upload second voice for bulk testing
    print("\n4. Testing second voice upload for bulk operations...")
    
    try:
        test_filename_2 = f"enhanced_test_2_{test_timestamp}.wav"
        files = {'voice_file': (test_filename_2, wav_header, 'audio/wav')}
        data = {
            'name': f"Enhanced Test 2",
            'description': 'Second test voice for bulk operations',
            'tags': 'test,enhanced,bulk',
            'folder_path': 'test_enhanced'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/voice",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Second voice uploaded - {result['filename']}")
            uploaded_filename_2 = result['filename']
        else:
            print(f"   FAILED: Second voice upload failed")
            uploaded_filename_2 = None
            
    except Exception as e:
        print(f"   ERROR: {e}")
        uploaded_filename_2 = None
    
    # Test 5: Single Voice Deletion (without confirm - should fail)
    print("\n5. Testing single voice deletion safety...")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/voice/{uploaded_filename}",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 400:
            print(f"   SUCCESS: Deletion correctly requires confirmation")
            print(f"   Safety message: {response.json().get('detail', 'No detail')}")
        else:
            print(f"   UNEXPECTED: Deletion without confirmation didn't fail (status {response.status_code})")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 6: Single Voice Deletion (with confirm)
    print("\n6. Testing confirmed single voice deletion...")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/voice/{uploaded_filename}?confirm=true",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Voice deleted")
            print(f"   Message: {result['message']}")
            print(f"   Deleted files: {result['deleted_files']}")
        else:
            print(f"   FAILED: Confirmed deletion failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 7: Bulk Deletion by folder (if second voice exists)
    if uploaded_filename_2:
        print("\n7. Testing bulk deletion by folder...")
        
        try:
            response = requests.delete(
                f"{API_BASE_URL}/api/v1/voices?folder=test_enhanced&confirm=true",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: Bulk deletion by folder")
                print(f"   Message: {result['message']}")
                print(f"   Deleted count: {result['deleted_count']}")
            else:
                print(f"   FAILED: Bulk deletion failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    else:
        print("\n7. SKIPPED: Bulk deletion test (second voice not available)")

    print("\n=== Enhanced Phase 10 Task 10.3 Complete Voice Management Tests Complete ===")


if __name__ == "__main__":
    test_enhanced_voice_management()

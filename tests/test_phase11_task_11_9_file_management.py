#!/usr/bin/env python3
"""
Test script for new file management endpoints in Task 11.9
Tests VC input upload, TTS with projects, and deletion endpoints
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:7860/api/v1"

def test_health():
    """Test basic connectivity"""
    print("Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        health = response.json()
        print(f"Server status: {health['status']}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def test_vc_input_upload():
    """Test VC input upload functionality"""
    print("\nTesting VC Input Upload...")
    
    # Test uploading to root folder
    test_file = Path("tests/media/alex.mp3")
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return False
    
    with open(test_file, 'rb') as f:
        files = {'vc_input_file': ('alex_test.mp3', f, 'audio/mp3')}
        data = {
            'text': 'Test audio file for VC input upload testing',
            'overwrite': 'true'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/vc_input", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            print(f"Upload successful: {result['message']}")
            print(f"   Filename: {result['filename']}")
            print(f"   Duration: {result['metadata']['duration_seconds']:.2f}s")
            return result['filename']
        except Exception as e:
            print(f"Upload failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return None

def test_vc_input_upload_with_project():
    """Test VC input upload with project folder"""
    print("\nTesting VC Input Upload with Project...")
    
    test_file = Path("tests/media/jamie-01.mp3")
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return False
    
    with open(test_file, 'rb') as f:
        files = {'vc_input_file': ('jamie_test.mp3', f, 'audio/mp3')}
        data = {
            'text': 'Jamie voice sample for project testing',
            'project': 'test_project',
            'overwrite': 'true'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/vc_input", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            print(f"Project upload successful: {result['message']}")
            print(f"   Folder: {result['metadata']['folder_path']}")
            return result['filename']
        except Exception as e:
            print(f"Project upload failed: {e}")
            return None

def test_tts_with_project():
    """Test TTS generation with project parameter"""
    print("\nTesting TTS with Project Parameter...")
    
    tts_data = {
        "text": "This is a test for project-based TTS generation.",
        "project": "test_tts_project",
        "export_formats": ["wav", "mp3"],
        "temperature": 0.75,
        "seed": 42
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tts", json=tts_data)
        response.raise_for_status()
        result = response.json()
        print(f"TTS generation successful")
        print(f"   Generated files: {len(result['output_files'])}")
        for file_info in result['output_files']:
            print(f"   - {file_info['filename']} ({file_info['format']})")
        return [f['filename'] for f in result['output_files']]
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return []

def test_list_endpoints():
    """Test listing endpoints to see uploaded/generated files"""
    print("\nTesting List Endpoints...")
    
    # Test VC inputs list
    try:
        response = requests.get(f"{BASE_URL}/vc_inputs")
        response.raise_for_status()
        vc_files = response.json()
        print(f"VC inputs list: {len(vc_files['files'])} files")
        for file_info in vc_files['files'][:3]:  # Show first 3
            print(f"   - {file_info['filename']} ({file_info.get('folder_path', 'root')})")
    except Exception as e:
        print(f"VC inputs list failed: {e}")
    
    # Test outputs list
    try:
        response = requests.get(f"{BASE_URL}/outputs")
        response.raise_for_status()
        output_files = response.json()
        print(f"Outputs list: {len(output_files['files'])} files")
        for file_info in output_files['files'][:3]:  # Show first 3
            print(f"   - {file_info['filename']} ({file_info.get('folder_path', 'root')})")
    except Exception as e:
        print(f"Outputs list failed: {e}")

def test_deletion_endpoints():
    """Test deletion endpoints"""
    print("\nTesting Deletion Endpoints...")
    
    # Test delete single VC input (with confirmation)
    try:
        # First check what files exist
        response = requests.get(f"{BASE_URL}/vc_inputs?search=alex_test")
        if response.ok:
            files = response.json()['files']
            if files:
                filename = files[0]['filename']
                delete_response = requests.delete(f"{BASE_URL}/vc_input/{filename}?confirm=true")
                delete_response.raise_for_status()
                result = delete_response.json()
                print(f"VC input deletion successful: {result['message']}")
            else:
                print("No alex_test files found to delete")
    except Exception as e:
        print(f"VC input deletion failed: {e}")
    
    # Test delete outputs in project folder
    try:
        delete_response = requests.delete(f"{BASE_URL}/outputs?project=test_tts_project&confirm=true")
        delete_response.raise_for_status()
        result = delete_response.json()
        print(f"Output project deletion successful: {result['message']}")
    except Exception as e:
        print(f"Output deletion failed: {e}")

def main():
    """Run all tests"""
    print("Testing File Management Endpoints (Task 11.9)")
    print("=" * 50)
    
    if not test_health():
        return
    
    # Test upload functionality
    uploaded_vc_file1 = test_vc_input_upload()
    uploaded_vc_file2 = test_vc_input_upload_with_project()
    
    # Test TTS with projects
    generated_files = test_tts_with_project()
    
    # Test list functionality
    test_list_endpoints()
    
    # Test deletion functionality
    test_deletion_endpoints()
    
    print("\nFile Management Endpoint Testing Complete!")

if __name__ == "__main__":
    main()

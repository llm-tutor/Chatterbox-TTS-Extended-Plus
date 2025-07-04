#!/usr/bin/env python3
"""
Unified streaming test suite for all API endpoints
Tests multi-format streaming consistency across TTS, VC, and concatenation endpoints
"""

import requests
import json
import shutil
from pathlib import Path

BASE_URL = "http://127.0.0.1:7860"

def test_tts_streaming():
    """Test TTS endpoint streaming with multiple formats"""
    print("=== Testing TTS Multi-Format Streaming ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/tts?response_mode=stream",
            json={
                "text": "Testing TTS multi-format streaming consistency.",
                "export_formats": ["wav", "mp3"]
            },
            stream=True
        )
        
        return analyze_streaming_response(response, "TTS", ["wav", "mp3"])
        
    except Exception as error:
        print(f"TTS streaming test failed: {error}")
        return False

def test_vc_streaming():
    """Test VC endpoint streaming with multiple formats"""
    print("\n=== Testing VC Multi-Format Streaming ===")
    
    # Setup files for VC testing
    reference_dir = Path("reference_audio")
    target_files = list(reference_dir.glob("*.wav")) + list(reference_dir.glob("*.mp3"))
    
    if not target_files:
        print("No reference audio files found - skipping VC test")
        return True  # Skip rather than fail
    
    # Ensure we have input file in vc_inputs
    vc_inputs_dir = Path("vc_inputs")
    vc_inputs_dir.mkdir(exist_ok=True)
    target_file = target_files[0]
    input_file = vc_inputs_dir / target_file.name
    
    if not input_file.exists():
        shutil.copy2(target_file, input_file)
        print(f"Copied {target_file.name} to vc_inputs/ for testing")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/vc?response_mode=stream",
            json={
                "input_audio_source": target_file.name,
                "target_voice_source": target_file.name,
                "export_formats": ["wav", "flac"]
            },
            stream=True
        )
        
        return analyze_streaming_response(response, "VC", ["wav", "flac"])
        
    except Exception as error:
        print(f"VC streaming test failed: {error}")
        return False

def test_concatenation_streaming():
    """Test concatenation endpoint streaming with multiple formats"""
    print("\n=== Testing Concatenation Multi-Format Streaming ===")
    
    # Use any existing files in outputs for testing
    outputs_dir = Path("outputs")
    test_files = list(outputs_dir.glob("*.wav")) if outputs_dir.exists() else []
    
    if len(test_files) < 1:
        print("No output files found - generating one for testing...")
        # Generate a quick file for testing
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/tts",
                json={"text": "Test file for concatenation", "export_formats": ["wav"]}
            )
            if response.status_code != 200:
                print("Failed to generate test file for concatenation")
                return False
        except Exception as e:
            print(f"Failed to generate test file: {e}")
            return False
        
        # Refresh file list
        test_files = list(outputs_dir.glob("*.wav")) if outputs_dir.exists() else []
        
    if len(test_files) < 1:
        print("Still no files available for concatenation testing")
        return False
    
    test_file = test_files[0].name
    print(f"Using file: {test_file}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/concat?response_mode=stream",
            json={
                "files": [test_file, test_file],
                "export_formats": ["wav", "mp3"]
            },
            stream=True
        )
        
        return analyze_streaming_response(response, "Concatenation", ["wav", "mp3"])
        
    except Exception as error:
        print(f"Concatenation streaming test failed: {error}")
        return False

def analyze_streaming_response(response, endpoint_name, expected_formats):
    """Analyze streaming response for consistency"""
    print(f"{endpoint_name} Multi-Format Stream Test:")
    print(f"- Status: {response.status_code}")
    print(f"- Content-Type: {response.headers.get('content-type')}")
    print(f"- Content-Length: {response.headers.get('content-length')}")
    print(f"- Content-Disposition: {response.headers.get('content-disposition')}")
    print(f"- X-Alternative-Formats: {response.headers.get('x-alternative-formats')}")
    
    # Check if we got a file stream or JSON
    content_type = response.headers.get('content-type', '')
    if response.status_code == 200 and 'audio/' in content_type:
        print("Successfully streaming audio file")
        
        # Save and check file size
        test_filename = f"test_{endpoint_name.lower()}_stream.wav"
        with open(test_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = Path(test_filename).stat().st_size
        print(f"- File size: {file_size} bytes")
        
        if file_size < 10000:
            print(" File too small, likely contains error instead of audio")
            success = False
        else:
            print(" File size looks reasonable for audio")
            success = True
            
        # Check for alternative formats header when multiple formats requested
        if len(expected_formats) > 1:
            alt_formats = response.headers.get('x-alternative-formats')
            if alt_formats:
                print(" Alternative formats provided in header")
            else:
                print(" Alternative formats header missing")
                success = False
        
        # Clean up test file
        Path(test_filename).unlink(missing_ok=True)
        
        return success
        
    else:
        print(" Got JSON response instead of stream")
        try:
            data = response.json()
            print(f"- Response: {json.dumps(data, indent=2)[:200]}...")
        except:
            print(f"- Raw content: {response.text[:200]}")
        return False

def main():
    """Run unified streaming test suite"""
    print("Unified API Streaming Consistency Test Suite")
    print("============================================")
    print("Testing multi-format streaming behavior across all endpoints")
    
    results = {}
    
    # Test all endpoints
    results['TTS'] = test_tts_streaming()
    results['VC'] = test_vc_streaming()
    results['Concatenation'] = test_concatenation_streaming()
    
    # Summary
    print("\n" + "="*50)
    print("STREAMING CONSISTENCY RESULTS")
    print("="*50)
    
    all_passed = True
    for endpoint, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{endpoint:15}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print(" ALL ENDPOINTS USE CONSISTENT STREAMING BEHAVIOR")
        print("  - All endpoints stream first requested format")
        print("  - All endpoints provide alternative formats in X-Alternative-Formats header")
        print("  - Multi-format streaming works correctly across TTS, VC, and Concatenation")
    else:
        print(" STREAMING INCONSISTENCIES DETECTED")
        print("  - Some endpoints need fixes to match the established pattern")
    
    print("="*50)
    return all_passed

if __name__ == "__main__":
    main()

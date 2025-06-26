#!/usr/bin/env python3
"""
Test file for Phase 11.5 Mixed Source Concatenation
Interactive test for POST /api/v1/concat/mixed endpoint

This test demonstrates mixing server files, uploaded files, and silence segments
in various configurations. Results are saved to tests/media/ for analysis.
"""

import requests
import json
import time
from pathlib import Path
import os

# Configuration
API_BASE = "http://127.0.0.1:7860"
BASE_DIR = Path("E:/Repos/Chatterbox-TTS-Extended-Plus")
TEST_MEDIA_DIR = BASE_DIR / "tests/media"
OUTPUTS_DIR = BASE_DIR / "outputs"

def setup_test_environment():
    """Ensure test media directory exists and show available files"""
    TEST_MEDIA_DIR.mkdir(exist_ok=True)
    print(f"Test media directory: {TEST_MEDIA_DIR.absolute()}")
    print(f"Server outputs directory: {OUTPUTS_DIR.absolute()}")
    
    # Show available test media files for upload (prefer smaller files)
    # Use simple audio files that are guaranteed to be small
    preferred_files = ["alex.mp3", "jamie-01.mp3", "jamie-02.mp3", "josh.mp3", "sean.mp3"]
    test_files = []
    
    for filename in preferred_files:
        file_path = TEST_MEDIA_DIR / filename
        if file_path.exists():
            test_files.append(file_path)
    
    # If we don't have enough preferred files, add some TTS files
    if len(test_files) < 3:
        tts_files = list(TEST_MEDIA_DIR.glob("Test-*-tts_*.wav")) + list(TEST_MEDIA_DIR.glob("tts_2025-*.wav"))
        for tts_file in tts_files:
            if len(test_files) >= 5:  # Limit total files
                break
            # Check file size to avoid huge files
            try:
                if tts_file.stat().st_size < 2 * 1024 * 1024:  # Under 2MB
                    test_files.append(tts_file)
            except OSError:
                continue
    
    print(f"\nAvailable small test files for upload ({len(test_files)} files):")
    for i, file in enumerate(test_files[:5]):  # Show first 5
        try:
            size_kb = file.stat().st_size / 1024
            print(f"  {i+1}. {file.name} ({size_kb:.1f} KB)")
        except OSError:
            print(f"  {i+1}. {file.name} (size unknown)")
    
    if len(test_files) > 5:
        print(f"  ... and {len(test_files) - 5} more files")
    
    return test_files

def get_server_files():
    """Get list of available small server files from outputs directory"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/outputs?page_size=20")
        if response.status_code == 200:
            data = response.json()
            # Filter for reasonably sized audio files (under 5MB to avoid massive concatenated files)
            small_files = []
            for f in data["files"]:
                if (f["filename"].endswith((".wav", ".mp3", ".flac")) and 
                    not f["filename"].startswith(("mixed_", "concat_")) and  # Avoid concatenated files
                    f.get("file_size_bytes", 999999999) < 5 * 1024 * 1024):  # Under 5MB
                    small_files.append(f["filename"])
            
            print(f"\nAvailable small server files in outputs/ ({len(small_files)} shown):")
            for i, filename in enumerate(small_files[:5]):  # Show first 5
                print(f"  {i+1}. {filename}")
            if len(small_files) > 5:
                print(f"  ... and {len(small_files) - 5} more files")
            return small_files
        else:
            print("Could not fetch server files")
            return []
    except Exception as e:
        print(f"Error fetching server files: {e}")
        return []

def test_server_files_only():
    """Test 1: Server files only with silence and processing"""
    print("\n" + "="*60)
    print("TEST 1: Server Files Only with Silence and Advanced Processing")
    print("="*60)
    
    server_files = get_server_files()
    if len(server_files) < 3:
        print("[WARNING]  Need at least 3 server files for this test")
        return False
    
    request_data = {
        "segments": [
            {"type": "server_file", "source": server_files[0]},
            {"type": "silence", "source": "(800ms)"},
            {"type": "server_file", "source": server_files[1]},
            {"type": "silence", "source": "(1.2s)"},
            {"type": "server_file", "source": server_files[2]}
        ],
        "export_formats": ["wav"],
        "normalize_levels": True,
        "crossfade_ms": 200,
        "trim": True,
        "trim_threshold_ms": 150,
        "output_filename": f"mixed_test_01_server_only_{int(time.time())}"
    }
    
    print(f"Using server files: {server_files[0]}, {server_files[1]}, {server_files[2]}")
    print("Features: Manual silence, crossfading, trimming, normalization")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data)},
            timeout=30  # Reduced timeout for smaller files
        )
        
        if response.status_code == 200:
            # Save the streamed audio
            timestamp = int(time.time())
            output_file = TEST_MEDIA_DIR / f"mixed_test_01_server_only_{timestamp}.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] Saved to: {output_file}")
            print(f"   File size: {len(response.content):,} bytes")
            return True
        else:
            print(f"[FAILED] Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] Exception: {e}")
        return False

def test_mixed_sources_with_uploads():
    """Test 2: Mixed sources with file uploads"""
    print("\n" + "="*60)
    print("TEST 2: Mixed Sources with File Uploads")
    print("="*60)
    
    # Use smaller TTS files instead of concatenated ones
    test_files = setup_test_environment()[:2]  # Get 2 smaller test files
    server_files = get_server_files()
    
    if len(test_files) < 2 or len(server_files) < 2:
        print("[WARNING]  Need at least 2 test files and 2 server files for this test")
        return False
    
    request_data = {
        "segments": [
            {"type": "server_file", "source": server_files[0]},
            {"type": "upload", "index": 0},
            {"type": "silence", "source": "(500ms)"},
            {"type": "upload", "index": 1},
            {"type": "server_file", "source": server_files[1]},
            {"type": "silence", "source": "(1s)"}
        ],
        "export_formats": ["wav", "mp3"],
        "normalize_levels": True,
        "crossfade_ms": 300,
        "pause_duration_ms": 0,  # Using manual silence instead
        "output_filename": f"mixed_test_02_uploads_{int(time.time())}"
    }
    
    print(f"Uploading: {test_files[0].name}, {test_files[1].name}")
    print(f"Using server files: {server_files[0]}, {server_files[1]}")
    print("Features: File uploads, manual silence, crossfading, multiple formats")
    
    try:
        files = [
            ("uploaded_files", (test_files[0].name, open(test_files[0], "rb"), "audio/wav")),
            ("uploaded_files", (test_files[1].name, open(test_files[1], "rb"), "audio/wav"))
        ]
        
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data)},
            files=files,
            timeout=30  # Reduced timeout for smaller files
        )
        
        # Close the files
        for _, file_tuple in files:
            file_tuple[1].close()
        
        if response.status_code == 200:
            # Save the streamed audio (primary format)
            timestamp = int(time.time())
            output_file = TEST_MEDIA_DIR / f"mixed_test_02_uploads_{timestamp}.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] Success! Saved to: {output_file}")
            print(f"   File size: {len(response.content):,} bytes")
            print("   Note: WAV and MP3 versions created in outputs/")
            return True
        else:
            print(f"[FAILED] Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAILED] Exception: {e}")
        return False

def test_natural_pauses_mode():
    """Test 3: Natural pauses mode (no manual silence)"""
    print("\n" + "="*60)
    print("TEST 3: Natural Pauses Mode")
    print("="*60)
    
    # Use smaller TTS files instead of concatenated ones
    test_files = setup_test_environment()[:1]  # Get 1 smaller test file
    server_files = get_server_files()
    
    if len(test_files) < 1 or len(server_files) < 3:
        print("[WARNING]  Need at least 1 test file and 3 server files for this test")
        return False
    
    request_data = {
        "segments": [
            {"type": "upload", "index": 0},
            {"type": "server_file", "source": server_files[0]},
            {"type": "server_file", "source": server_files[1]},
            {"type": "server_file", "source": server_files[2]}
        ],
        "export_formats": ["wav"],
        "normalize_levels": True,
        "pause_duration_ms": 700,    # Natural pauses between consecutive audio files
        "pause_variation_ms": 150,   # Random variation
        "crossfade_ms": 0,           # No crossfading
        "output_filename": f"mixed_test_03_natural_pauses_{int(time.time())}"
    }
    
    print(f"Uploading: {test_files[0].name}")
    print(f"Using server files: {server_files[0]}, {server_files[1]}, {server_files[2]}")
    print("Features: Natural pauses with variation, no manual silence")
    
    try:
        files = [
            ("uploaded_files", (test_files[0].name, open(test_files[0], "rb"), "audio/wav"))
        ]
        
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data)},
            files=files,
            timeout=30  # Reduced timeout for smaller files
        )
        
        # Close the file
        files[0][1][1].close()
        
        if response.status_code == 200:
            # Save the streamed audio
            timestamp = int(time.time())
            output_file = TEST_MEDIA_DIR / f"mixed_test_03_natural_pauses_{timestamp}.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] Success! Saved to: {output_file}")
            print(f"   File size: {len(response.content):,} bytes")
            return True
        else:
            print(f"[FAILED] Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAILED] Exception: {e}")
        return False

def test_complex_scenario():
    """Test 4: Complex scenario with many files and advanced processing"""
    print("\n" + "="*60)
    print("TEST 4: Complex Scenario - Many Files with Advanced Processing")
    print("="*60)
    
    # Use smaller TTS files instead of concatenated ones
    test_files = setup_test_environment()[:3]  # Get 3 smaller test files
    server_files = get_server_files()
    
    if len(test_files) < 3 or len(server_files) < 4:
        print("[WARNING]  Need at least 3 test files and 4 server files for this test")
        return False
    
    request_data = {
        "segments": [
            {"type": "silence", "source": "(300ms)"},
            {"type": "server_file", "source": server_files[0]},
            {"type": "upload", "index": 0},
            {"type": "silence", "source": "(600ms)"},
            {"type": "upload", "index": 1},
            {"type": "server_file", "source": server_files[1]},
            {"type": "upload", "index": 2},
            {"type": "silence", "source": "(400ms)"},
            {"type": "server_file", "source": server_files[2]},
            {"type": "server_file", "source": server_files[3]},
            {"type": "silence", "source": "(1s)"}
        ],
        "export_formats": ["wav", "mp3", "flac"],
        "normalize_levels": True,
        "crossfade_ms": 150,
        "trim": True,
        "trim_threshold_ms": 200,
        "output_filename": f"mixed_test_04_complex_{int(time.time())}"
    }
    
    print(f"Uploading: {test_files[0].name}, {test_files[1].name}, {test_files[2].name}")
    print(f"Using server files: {server_files[0]}, {server_files[1]}, {server_files[2]}, {server_files[3]}")
    print("Features: 11 segments, 3 uploads, 4 server files, 4 silence segments")
    print("Processing: Trimming, crossfading, normalization, 3 output formats")
    
    try:
        files = [
            ("uploaded_files", (test_files[0].name, open(test_files[0], "rb"), "audio/wav")),
            ("uploaded_files", (test_files[1].name, open(test_files[1], "rb"), "audio/wav")),
            ("uploaded_files", (test_files[2].name, open(test_files[2], "rb"), "audio/wav"))
        ]
        
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data)},
            files=files,
            timeout=90
        )
        
        # Close the files
        for _, file_tuple in files:
            file_tuple[1].close()
        
        if response.status_code == 200:
            # Save the streamed audio
            timestamp = int(time.time())
            output_file = TEST_MEDIA_DIR / f"mixed_test_04_complex_{timestamp}.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] Success! Saved to: {output_file}")
            print(f"   File size: {len(response.content):,} bytes")
            print("   Note: WAV, MP3, and FLAC versions created in outputs/")
            return True
        else:
            print(f"[FAILED] Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAILED] Exception: {e}")
        return False

def test_url_response_mode():
    """Test 5: URL response mode (returns JSON instead of streaming)"""
    print("\n" + "="*60)
    print("TEST 5: URL Response Mode")
    print("="*60)
    
    server_files = get_server_files()
    
    if len(server_files) < 2:
        print("[WARNING]  Need at least 2 server files for this test")
        return False
    
    request_data = {
        "segments": [
            {"type": "server_file", "source": server_files[0]},
            {"type": "silence", "source": "(500ms)"},
            {"type": "server_file", "source": server_files[1]}
        ],
        "export_formats": ["wav"],
        "normalize_levels": True,
        "output_filename": f"mixed_test_05_url_mode_{int(time.time())}"
    }
    
    print(f"Using server files: {server_files[0]}, {server_files[1]}")
    print("Features: URL response mode (returns JSON with metadata)")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed?response_mode=url",
            data={"request_json": json.dumps(request_data)},
            timeout=30  # Reduced timeout for smaller files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Success! Response JSON:")
            print(json.dumps(result, indent=2))
            print(f"\nGenerated files: {result.get('output_files', [])}")
            print(f"Processing time: {result.get('processing_time_seconds', 0):.2f}s")
            print(f"Total duration: {result.get('total_duration_seconds', 0):.2f}s")
            return True
        else:
            print(f"[FAILED] Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAILED] Exception: {e}")
        return False

def test_validation_errors():
    """Test 6: Validation error scenarios"""
    print("\n" + "="*60)
    print("TEST 6: Validation Error Scenarios")
    print("="*60)
    
    print("Testing various validation scenarios...")
    
    # Test 1: Missing upload file
    request_data_1 = {
        "segments": [
            {"type": "upload", "index": 0}  # No file uploaded
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data_1)},
            timeout=10
        )
        print(f"Missing upload test: {response.status_code} ({'[SUCCESS] Expected' if response.status_code == 400 else '[FAILED] Unexpected'})")
    except Exception as e:
        print(f"Missing upload test failed: {e}")
    
    # Test 2: Non-existent server file
    request_data_2 = {
        "segments": [
            {"type": "server_file", "source": "nonexistent_file_12345.wav"}
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data_2)},
            timeout=10
        )
        print(f"Non-existent file test: {response.status_code} ({'[SUCCESS] Expected' if response.status_code == 404 else '[FAILED] Unexpected'})")
    except Exception as e:
        print(f"Non-existent file test failed: {e}")
    
    # Test 3: Invalid silence notation
    request_data_3 = {
        "segments": [
            {"type": "silence", "source": "(invalid_format)"}
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/concat/mixed",
            data={"request_json": json.dumps(request_data_3)},
            timeout=10
        )
        print(f"Invalid silence test: {response.status_code} ({'[SUCCESS] Expected' if response.status_code in [400, 422] else '[FAILED] Unexpected'})")
    except Exception as e:
        print(f"Invalid silence test failed: {e}")
    
    return True

def main():
    """Run all mixed concatenation tests"""
    print("Mixed Source Concatenation Test Suite")
    print("Phase 11.5 - POST /api/v1/concat/mixed")
    print("=" * 60)
    
    setup_test_environment()
    
    tests = [
        ("Server Files Only", test_server_files_only),
        ("Mixed Sources with Uploads", test_mixed_sources_with_uploads),
        ("Natural Pauses Mode", test_natural_pauses_mode),
        ("Complex Scenario", test_complex_scenario),
        ("URL Response Mode", test_url_response_mode),
        ("Validation Errors", test_validation_errors)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            print(f"\n[Running]: {name}")
            if test_func():
                passed += 1
                print(f"[PASSED] {name}: PASSED")
            else:
                print(f"[FAILED] {name}: FAILED")
        except Exception as e:
            print(f"[EXCEPTION] {name}: EXCEPTION - {e}")
    
    print("\n" + "="*60)
    print(f"TEST SUITE SUMMARY")
    print("="*60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("[COMPLETE] ALL TESTS PASSED!")
        print("\nGenerated test files are saved in tests/media/ for analysis:")
        test_output_files = list(TEST_MEDIA_DIR.glob("mixed_test_*.wav"))
        for file in test_output_files:
            if file.exists():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  [FILE] {file.name} ({size_mb:.2f} MB)")
    else:
        print("[WARNING]  Some tests failed. Check the output above for details.")
    
    print(f"\nAPI Endpoint: POST {API_BASE}/api/v1/concat/mixed")
    print("Documentation: docs/api/endpoints/concatenation.md")

if __name__ == "__main__":
    main()

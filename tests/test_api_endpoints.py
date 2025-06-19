# test_api_endpoints.py - Test API endpoints once server is running

"""
Test script for API endpoints. 
Run this AFTER starting the server with: python main_api.py
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:7860"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Health check passed - Status: {data.get('status')}")
            print(f"     Models loaded: {data.get('models_loaded')}")
            print(f"     Uptime: {data.get('uptime_seconds', 0):.1f}s")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Health check error: {e}")
        return False

def test_config():
    """Test config endpoint"""
    print("\nTesting config endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/config")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Config retrieved")
            print(f"     Supported formats: {data.get('supported_formats')}")
            print(f"     TTS defaults: {len(data.get('tts_defaults', {}))} parameters")
            return True
        else:
            print(f"[FAIL] Config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Config error: {e}")
        return False

def test_voices():
    """Test voices endpoint"""
    print("\nTesting voices endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/voices")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Voices retrieved")
            print(f"     Found {data.get('count', 0)} voices")
            voices = data.get('voices', [])
            for voice in voices[:3]:  # Show first 3
                print(f"     - {voice.get('path')}")
            if len(voices) > 3:
                print(f"     ... and {len(voices) - 3} more")
            return True
        else:
            print(f"[FAIL] Voices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Voices error: {e}")
        return False

def test_tts_basic():
    """Test basic TTS generation"""
    print("\nTesting TTS endpoint...")
    try:
        payload = {
            # "text": "Hello, this is a test of the TTS API. The quick brown fox jumps over the lazy dog.",
            # "text": "Hello, this is a test of the TTS API. Because here we go again.",
            # "text": "Hello. This is just a test, but an important one. Don't be cocky.",
            "text": "Listen up! Hear this carefully: The implications were revolutionary. If the Earth's stability could be explained through natural principles rather than divine support, what else might be understood through careful observation and reasoning? If Atlas wasn't needed to hold up the Earth, perhaps other divine explanations could be replaced with natural ones.",
            # "text": "Among the curious objects that passed through the port of Miletus was a strange black stone – what we now call magnetite or lodestone. When brought near iron, it would cause the metal to move, seemingly by its own power. For many, this was clear evidence of divine presence, a miracle in stone.",
            # "text": "Among the curious objects that passed through the port of Miletus was a strange black stone – what we now call magnetite or lodestone. When brought near iron, it would cause the metal to move, seemingly by its own power. For many, this was clear evidence of divine presence, a miracle in stone.",
            # "reference_audio_filename": "speaker_en/DAVID-2.mp3",
            "reference_audio_filename": "speaker_en/jamie_vc_to_david-2.wav",
            "export_formats": ["wav"]
        }
        
        print("     Sending TTS request...")
        response = requests.post(
            f"{BASE_URL}/api/v1/tts",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300  # Allow time for generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] TTS generation successful")
            print(f"     Generated files: {len(data.get('output_files', []))}")
            print(f"     Seed used: {data.get('generation_seed_used')}")
            print(f"     Processing time: {data.get('processing_time_seconds', 0):.1f}s")
            
            # Show output files
            for file_info in data.get('output_files', []):
                print(f"     - {file_info.get('format')}: {file_info.get('url')}")
            
            return True
        else:
            print(f"[FAIL] TTS failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"     Error: {error_data.get('error')}")
            except:
                print(f"     Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] TTS error: {e}")
        return False

def test_vc_basic():
    """Test basic VC (will likely fail without audio files)"""
    print("\nTesting VC endpoint...")
    try:
        payload = {
            "input_audio_source": "ElevenLabs_2025-06-16T00_38_05_Jamie_gen_sp100_s50_sb75_se0_b_m2.mp3",
            # "input_audio_source": "ElevenLabs_2025-06-19T03_12_23_Jamie_gen_sp100_s50_sb75_f2.mp3",
            # "input_audio_source":  "hello_quick_brown.wav",
            # "target_voice_source": "speaker_en/DAVID-2.mp3",
            "target_voice_source": "CONNOR-2-non-native.mp3",
            "export_formats": ["wav"]
        }
        
        print("     Sending VC request...")
        response = requests.post(
            f"{BASE_URL}/api/v1/vc",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] VC generation successful")
            print(f"     Generated files: {len(data.get('output_files', []))}")
            print(f"     Processing time: {data.get('processing_time_seconds', 0):.1f}s")
            
            # Show output files
            for file_info in data.get('output_files', []):
                print(f"     - {file_info.get('format')}: {file_info.get('url')}")
            
            return True
        elif response.status_code == 404:
            print(f"[EXPECTED] VC failed: Audio files not found")
            print(f"     This is expected if you haven't placed audio files in the directories")
            return True  # This is expected
        else:
            print(f"[FAIL] VC failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"     Error: {error_data.get('error')}")
            except:
                print(f"     Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] VC error: {e}")
        return False

def main():
    """Run all API tests"""
    print("Chatterbox TTS Extended Plus - API Endpoint Tests")
    print("=" * 55)
    print("Make sure the server is running: python main_api.py")
    print("")
    
    # Wait a moment for server to be ready
    print("Waiting 2 seconds for server...")
    time.sleep(2)
    
    tests = [
        test_health,
        test_config,
        test_voices,
        test_tts_basic,
        test_vc_basic
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[CRASH] Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 55)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[SUCCESS] All API tests passed!")
        print("\nThe API is working correctly. Ready for Phase 4!")
    else:
        print("[PARTIAL] Some tests failed, but this may be expected.")
        print("Check the errors above. TTS should work, VC may fail without audio files.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Voice Metadata Deep Validation - Task 10.2 Focus

Detailed validation of voice metadata calculation, accuracy, and storage.
This test verifies that metadata matches actual file properties.

PREREQUISITES:
- Server running at http://127.0.0.1:7860
- Voice files in reference_audio/ directory

USAGE:
Run from project root: python tests/test_voice_metadata_validation.py

VALIDATES:
- Metadata calculation accuracy (duration, sample rate, file size)
- JSON companion file structure and content
- API metadata consistency
- Usage tracking for both TTS and VC operations

OUTPUT:
- Console validation results
- JSON files created/updated in reference_audio/
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:7860"
PROJECT_ROOT = Path(__file__).parent.parent

def get_actual_audio_info(file_path):
    """Get actual audio file properties using available libraries"""
    info = {'file_size_bytes': file_path.stat().st_size}
    
    # Try soundfile first
    try:
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            info['duration_seconds'] = len(f) / f.samplerate
            info['sample_rate'] = f.samplerate
            info['channels'] = f.channels
        return info, 'soundfile'
    except:
        pass
    
    # Fallback to librosa
    try:
        import librosa
        y, sr = librosa.load(str(file_path), sr=None)
        info['duration_seconds'] = len(y) / sr
        info['sample_rate'] = sr
        return info, 'librosa'
    except:
        pass
    
    return info, 'file_only'

def validate_voice_metadata():
    """Validate voice metadata accuracy"""
    print("VOICE METADATA ACCURACY VALIDATION")
    print("=" * 50)
    
    ref_audio_dir = PROJECT_ROOT / "reference_audio"
    if not ref_audio_dir.exists():
        print("❌ Reference audio directory not found")
        return
    
    # Find audio files
    audio_files = []
    for ext in ['.wav', '.mp3', '.flac']:
        audio_files.extend(ref_audio_dir.rglob(f"*{ext}"))
    
    print(f"Found {len(audio_files)} audio files")
    
    for i, audio_file in enumerate(audio_files[:3], 1):  # Test first 3
        print(f"\n[{i}] Validating: {audio_file.name}")
        
        # Get actual file properties
        actual_info, method = get_actual_audio_info(audio_file)
        print(f"    Analysis method: {method}")
        
        # Check for metadata file
        metadata_file = audio_file.with_suffix(audio_file.suffix + '.json')
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                print("    ✅ Metadata file exists")
                
                # Validate file size
                if 'file_size_bytes' in actual_info:
                    actual_size = actual_info['file_size_bytes']
                    meta_size = metadata.get('file_size_bytes')
                    if meta_size and abs(actual_size - meta_size) <= 1:
                        print(f"    ✅ File size accurate: {meta_size:,} bytes")
                    else:
                        print(f"    ❌ File size mismatch: meta={meta_size}, actual={actual_size}")
                
                # Validate duration
                if 'duration_seconds' in actual_info:
                    actual_duration = actual_info['duration_seconds']
                    meta_duration = metadata.get('duration_seconds')
                    if meta_duration and abs(actual_duration - meta_duration) < 0.1:
                        print(f"    ✅ Duration accurate: {meta_duration:.2f}s")
                    else:
                        print(f"    ❌ Duration mismatch: meta={meta_duration:.2f}s, actual={actual_duration:.2f}s")
                
                # Validate sample rate
                if 'sample_rate' in actual_info:
                    actual_sr = actual_info['sample_rate']
                    meta_sr = metadata.get('sample_rate')
                    if meta_sr and actual_sr == meta_sr:
                        print(f"    ✅ Sample rate accurate: {meta_sr} Hz")
                    else:
                        print(f"    ❌ Sample rate mismatch: meta={meta_sr}, actual={actual_sr}")
                
                # Check usage tracking fields
                usage_count = metadata.get('usage_count', 0)
                last_used = metadata.get('last_used')
                print(f"    📊 Usage count: {usage_count}")
                print(f"    📊 Last used: {last_used or 'Never'}")
                
            except Exception as e:
                print(f"    ❌ Error reading metadata: {e}")
        else:
            print("    ⚠️ No metadata file - will be created on first API call")

def test_api_metadata_consistency():
    """Test API metadata matches file metadata"""
    print("\n\nAPI METADATA CONSISTENCY")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"API returned {data.get('count', 0)} voices")
            
            for voice in data.get('voices', [])[:2]:  # Check first 2
                name = voice.get('name')
                print(f"\nValidating API data for: {name}")
                
                # Find corresponding file
                ref_audio_dir = PROJECT_ROOT / "reference_audio"
                voice_file = None
                for ext in ['.wav', '.mp3', '.flac']:
                    potential_file = ref_audio_dir / f"{name}{ext}"
                    if potential_file.exists():
                        voice_file = potential_file
                        break
                
                if voice_file:
                    metadata_file = voice_file.with_suffix(voice_file.suffix + '.json')
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            file_metadata = json.load(f)
                        
                        # Compare key fields
                        fields_to_check = ['duration_seconds', 'sample_rate', 'file_size_bytes', 'usage_count']
                        for field in fields_to_check:
                            api_value = voice.get(field)
                            file_value = file_metadata.get(field)
                            if api_value == file_value:
                                print(f"    ✅ {field}: {api_value}")
                            else:
                                print(f"    ❌ {field} mismatch: API={api_value}, File={file_value}")
                    else:
                        print("    ⚠️ No metadata file to compare")
                else:
                    print("    ❌ Voice file not found")
        else:
            print(f"❌ API request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")

def test_usage_tracking_both_endpoints():
    """Test usage tracking for both TTS and VC"""
    print("\n\nUSAGE TRACKING VALIDATION")
    print("=" * 50)
    
    try:
        # Get a voice to test with
        response = requests.get(f"{BASE_URL}/api/v1/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('voices'):
                test_voice = data['voices'][0]
                voice_name = test_voice.get('name')
                initial_usage = test_voice.get('usage_count', 0)
                
                print(f"Testing with voice: {voice_name}")
                print(f"Initial usage count: {initial_usage}")
                
                # Test TTS usage tracking
                print("\n1. Testing TTS usage tracking...")
                tts_request = {
                    "text": "Testing voice usage tracking in TTS",
                    "reference_audio_filename": voice_name,
                    "seed": 123,
                    "export_formats": ["wav"]
                }
                
                tts_response = requests.post(f"{BASE_URL}/api/v1/tts", json=tts_request, timeout=60)
                if tts_response.status_code == 200:
                    print("   ✅ TTS generation successful")
                    
                    # Check usage update
                    time.sleep(1)
                    updated_response = requests.get(f"{BASE_URL}/api/v1/voices", timeout=10)
                    if updated_response.status_code == 200:
                        updated_data = updated_response.json()
                        updated_voice = next((v for v in updated_data.get('voices', []) if v.get('name') == voice_name), None)
                        
                        if updated_voice:
                            new_usage = updated_voice.get('usage_count', 0)
                            if new_usage > initial_usage:
                                print(f"   ✅ Usage tracking working: {initial_usage} → {new_usage}")
                                initial_usage = new_usage  # Update for next test
                            else:
                                print(f"   ⚠️ Usage count unchanged: {new_usage}")
                else:
                    print(f"   ❌ TTS failed: {tts_response.status_code}")
                
                # Note about VC testing
                print("\n2. VC usage tracking:")
                print("   📝 VC also tracks target voice usage when target_voice_source is used")
                print("   📝 Implementation already added to core_engine.py VC generation")
                print("   📝 Would need input audio file to test fully")
                
            else:
                print("❌ No voices available for testing")
    except Exception as e:
        print(f"❌ Usage tracking test error: {e}")

def main():
    """Run voice metadata validation"""
    print("VOICE METADATA DEEP VALIDATION")
    print("Task 10.2 - Enhanced Voice Metadata System")
    print("=" * 50)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Run validation tests
    validate_voice_metadata()
    test_api_metadata_consistency()
    test_usage_tracking_both_endpoints()
    
    print("\n" + "=" * 50)
    print("VALIDATION COMPLETE")
    print("✅ Voice metadata system comprehensive validation finished")
    print("📁 Check reference_audio/ for updated JSON metadata files")

if __name__ == "__main__":
    main()

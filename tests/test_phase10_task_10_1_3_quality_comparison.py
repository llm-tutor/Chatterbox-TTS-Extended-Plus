#!/usr/bin/env python3
"""
Enhanced Speed Factor Quality Comparison Test

Focused on the main use case: slowing down accelerated TTS speech
Tests both slower (0.7x, 0.8x) and faster (1.2x, 1.3x) speeds
Configurable library selection for easy comparison
"""

import time
import requests
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

API_BASE = "http://127.0.0.1:7860/api/v1"

# CONFIGURATION - Edit these to test different libraries
TEST_LIBRARY = "audiostretchy"  # Options: "audiostretchy", "pyrubberband", "librosa", "auto"
REFERENCE_VOICE = "speaker_en/jamie_vc_to_david-2.wav"
TEST_TEXT = "Testing enhanced speed factor quality with various speed adjustments for optimal speech pacing."

# Test speeds - focused on real-world use cases
TEST_SPEEDS = [
    (0.7, "Very_Slow"),     # Significantly slow down fast TTS
    (0.8, "Slow"),          # Moderately slow down TTS  
    (1.2, "Fast"),          # Speed up slow speech
    (1.3, "Very_Fast"),     # Significantly speed up
]

def test_speed_factor(speed_factor, speed_name, library):
    """Test a specific speed factor and library combination"""
    print(f"\n--- Testing {library} @ {speed_factor}x ({speed_name}) ---")
    
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": TEST_TEXT,
            "reference_audio_filename": REFERENCE_VOICE,
            "speed_factor": speed_factor,
            "speed_factor_library": library,
            "export_formats": ["wav"]
        }, timeout=120)
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            output_files = result.get('output_files', [])
            
            if output_files:
                # Get the WAV file path
                wav_file = next((f for f in output_files if f['format'] == 'wav'), None)
                if wav_file:
                    source_path = Path(wav_file['path'])
                    
                    # Create timestamp-based filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    descriptive_name = f"phase10_1_3_{library}_{speed_factor}x_{speed_name.lower()}_{timestamp}.wav"
                    
                    # Copy to tests/media
                    tests_media_dir = Path("tests/media")
                    tests_media_dir.mkdir(exist_ok=True)
                    destination = tests_media_dir / descriptive_name
                    
                    try:
                        shutil.copy2(source_path, destination)
                        print(f"SUCCESS: {elapsed:.1f}s")
                        print(f"Saved to: tests/media/{descriptive_name}")
                        return True, elapsed, str(destination)
                    except Exception as e:
                        print(f"SUCCESS: {elapsed:.1f}s (copy failed: {e})")
                        print(f"Original: {source_path}")
                        return True, elapsed, str(source_path)
                else:
                    print(f"SUCCESS: {elapsed:.1f}s (no WAV file found)")
                    return True, elapsed, None
            else:
                print(f"SUCCESS: {elapsed:.1f}s (no output files)")
                return True, elapsed, None
            
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False, elapsed, None
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"FAILED: {e}")
        return False, elapsed, None

def main():
    print("Enhanced Speed Factor Quality Comparison Test")
    print("=" * 60)
    print(f"Library: {TEST_LIBRARY}")
    print(f"Test Text: {TEST_TEXT}")
    print(f"Reference Voice: {REFERENCE_VOICE}")
    print(f"Testing {len(TEST_SPEEDS)} speed factors")
    print("=" * 60)
    
    results = {}
    generated_files = []
    
    for speed_factor, speed_name in TEST_SPEEDS:
        success, elapsed, file_path = test_speed_factor(speed_factor, speed_name, TEST_LIBRARY)
        
        results[f"{speed_factor}x"] = {
            'speed_factor': speed_factor,
            'speed_name': speed_name,
            'library': TEST_LIBRARY,
            'success': success,
            'time': elapsed,
            'file': file_path
        }
        
        if file_path:
            generated_files.append((speed_factor, speed_name, Path(file_path).name))
        
        # Short pause between tests
        time.sleep(1)
    
    # Results Summary
    print(f"\n" + "=" * 60)
    print("SPEED FACTOR QUALITY TEST RESULTS")
    print("=" * 60)
    
    successful_tests = []
    for speed_key, result in results.items():
        status = "PASS" if result['success'] else "FAIL"
        print(f"{status} {speed_key} ({result['speed_name']}): {result['time']:.1f}s")
        if result['success']:
            successful_tests.append(result)
    
    print(f"\nSUCCESS RATE: {len(successful_tests)}/{len(TEST_SPEEDS)} tests passed")
    
    # Performance Analysis
    if successful_tests:
        times = [r['time'] for r in successful_tests]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\nPERFORMANCE ANALYSIS ({TEST_LIBRARY}):")
        print(f"Average time: {avg_time:.1f}s")
        print(f"Fastest: {min_time:.1f}s")
        print(f"Slowest: {max_time:.1f}s")
        print(f"Range: {max_time - min_time:.1f}s")
    
    # Generated Files
    if generated_files:
        print(f"\nGENERATED AUDIO FILES (tests/media/):")
        print("Listen to compare quality at different speeds:")
        for speed, name, filename in generated_files:
            print(f"  {speed}x ({name}): {filename}")
        
        print(f"\nUSAGE RECOMMENDATION:")
        print(f"For slowing down fast TTS: Try 0.7x-0.8x speeds")
        print(f"For speeding up slow speech: Try 1.2x-1.3x speeds")
        print(f"Current library: {TEST_LIBRARY}")
        print(f"To test different library: Edit TEST_LIBRARY in the script")
    
    return len(successful_tests) == len(TEST_SPEEDS)

if __name__ == "__main__":
    print(f"Configuration:")
    print(f"  Library: {TEST_LIBRARY}")
    print(f"  Speeds: {[f'{s}x' for s, _ in TEST_SPEEDS]}")
    print(f"\nTo test different library, edit TEST_LIBRARY at top of script")
    print(f"Available options: 'audiostretchy', 'pyrubberband', 'librosa', 'auto'")
    print()
    
    success = main()
    sys.exit(0 if success else 1)

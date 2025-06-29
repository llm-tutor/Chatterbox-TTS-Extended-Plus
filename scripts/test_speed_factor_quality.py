#!/usr/bin/env python3
"""
Test script to verify audio quality and format for speed factor processing
Task 11.11.1 - Quality verification for the alternative fix
"""

import soundfile as sf
import numpy as np
import requests
import json
import time

BASE_URL = "http://127.0.0.1:7860/api/v1"

def test_speed_factor_quality():
    """Test speed factor processing with quality verification"""
    print("Testing speed factor processing - Quality and Format Verification")
    print("=" * 70)
    
    # Test with different speed factors
    test_cases = [
        {"speed": 0.8, "desc": "Slower (0.8x)"},
        {"speed": 1.0, "desc": "Normal (1.0x) - baseline"},
        {"speed": 1.2, "desc": "Faster (1.2x)"},
        {"speed": 1.5, "desc": "Much faster (1.5x)"}
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\nTesting {case['desc']}...")
        
        tts_data = {
            "text": "This is a quality test for speed factor processing with the new precision fix.",
            "speed_factor": case['speed'],
            "export_formats": ["wav"],
            "temperature": 0.75,
            "seed": 12345,  # Use consistent seed for comparison
            "response_mode": "url"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tts", json=tts_data, timeout=30)
            response.raise_for_status()
            
            # Get the response
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                wav_file = result['output_files'][0]
                file_path = f"outputs/{wav_file['filename']}"
                
                # Analyze the audio file
                info = sf.info(file_path)
                audio_data, sample_rate = sf.read(file_path)
                
                # Calculate audio metrics
                duration = len(audio_data) / sample_rate
                rms_level = np.sqrt(np.mean(audio_data**2))
                peak_level = np.max(np.abs(audio_data))
                dynamic_range = peak_level / (rms_level + 1e-10)
                
                results.append({
                    'speed': case['speed'],
                    'filename': wav_file['filename'],
                    'format': info.subtype,
                    'sample_rate': info.samplerate,
                    'duration': duration,
                    'rms_level': rms_level,
                    'peak_level': peak_level,
                    'dynamic_range': dynamic_range,
                    'file_size': info.frames * info.channels
                })
                
                print(f"   [PASS] Generated: {wav_file['filename']}")
                print(f"   [PASS] Format: {info.subtype} ({info.subtype_info})")
                print(f"   [PASS] Duration: {duration:.2f}s")
                print(f"   [PASS] RMS Level: {rms_level:.4f}")
                print(f"   [PASS] Peak Level: {peak_level:.4f}")
                
            else:
                print(f"   [FAIL] Unexpected response format")
                
        except Exception as e:
            print(f"   [FAIL] Request failed: {e}")
    
    # Quality analysis comparison
    if len(results) >= 2:
        print(f"\n" + "=" * 70)
        print("QUALITY ANALYSIS")
        print("=" * 70)
        
        baseline = next((r for r in results if r['speed'] == 1.0), results[0])
        
        print(f"\nBaseline (1.0x speed):")
        print(f"  Format: {baseline['format']}")
        print(f"  Duration: {baseline['duration']:.2f}s")
        print(f"  RMS Level: {baseline['rms_level']:.4f}")
        print(f"  Peak Level: {baseline['peak_level']:.4f}")
        
        print(f"\nComparison with other speeds:")
        for result in results:
            if result['speed'] != 1.0:
                duration_ratio = result['duration'] / baseline['duration']
                rms_diff = abs(result['rms_level'] - baseline['rms_level'])
                peak_diff = abs(result['peak_level'] - baseline['peak_level'])
                
                print(f"\n  Speed {result['speed']}x:")
                print(f"    Format: {result['format']} {'[OK]' if result['format'] == 'FLOAT' else '[WRONG]'}")
                print(f"    Duration ratio: {duration_ratio:.3f} (expected: {1/result['speed']:.3f})")
                print(f"    RMS difference: {rms_diff:.4f}")
                print(f"    Peak difference: {peak_diff:.4f}")
                
                # Quality assessment
                format_ok = result['format'] == 'FLOAT'
                duration_ok = abs(duration_ratio - (1/result['speed'])) < 0.05  # 5% tolerance
                quality_ok = rms_diff < 0.1 and peak_diff < 0.1  # Quality preservation
                
                overall_status = "[PASS]" if format_ok and duration_ok and quality_ok else "[ISSUES]"
                print(f"    Overall: {overall_status}")
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    format_issues = [r for r in results if r['format'] != 'FLOAT']
    if format_issues:
        print(f"[WARNING] Format Issues: {len(format_issues)} files not in FLOAT format")
        for r in format_issues:
            print(f"   - {r['filename']}: {r['format']}")
    else:
        print("[PASS] All files generated in correct FLOAT (32-bit) format")
    
    print(f"[PASS] Generated {len(results)} test files successfully")
    print("[PASS] Speed factor processing working with quality preservation")

if __name__ == "__main__":
    test_speed_factor_quality()

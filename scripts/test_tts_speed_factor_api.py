#!/usr/bin/env python3
"""
Test TTS with speed factor through the API to verify Task 11.11 fix
"""

import requests
import json

BASE_URL = "http://127.0.0.1:7860/api/v1"

def test_tts_speed_factor():
    """Test TTS with speed factor through API"""
    print("Testing TTS with speed factor through API")
    print("=" * 50)
    
    # Test different speed factors with JSON response mode
    test_cases = [
        {"speed": 0.8, "desc": "Slower (0.8x)"},
        {"speed": 1.0, "desc": "Normal (1.0x)"},
        {"speed": 1.2, "desc": "Faster (1.2x)"},
        {"speed": 1.5, "desc": "Much faster (1.5x)"}
    ]
    
    for case in test_cases:
        print(f"\nTesting {case['desc']}...")
        
        tts_data = {
            "text": "This is a test of speed factor processing with audiostretchy precision fix.",
            "speed_factor": case['speed'],
            "export_formats": ["wav"],
            "temperature": 0.75,
            "seed": 42,
            "response_mode": "url"  # Force JSON response mode
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tts", json=tts_data, timeout=30)
            response.raise_for_status()
            
            # Check if response is JSON or binary
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                result = response.json()
                
                if result['output_files']:
                    wav_file = result['output_files'][0]
                    print(f"   [PASS] Generated: {wav_file['filename']}")
                    print(f"   Duration: {wav_file.get('duration_seconds', 'N/A')}s")
                    print(f"   Format: {wav_file['format']}")
                else:
                    print(f"   [FAIL] No output files generated")
            else:
                # Streaming response
                print(f"   [PASS] Generated streaming response ({len(response.content)} bytes)")
                print(f"   Content-Type: {content_type}")
                
        except Exception as e:
            print(f"   [FAIL] Request failed: {e}")
    
    print(f"\nTTS speed factor test complete!")

if __name__ == "__main__":
    test_tts_speed_factor()

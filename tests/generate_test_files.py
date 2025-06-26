#!/usr/bin/env python3
"""
Generate small test files for mixed concatenation testing
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:7860"

def generate_test_files():
    """Generate a few small TTS files for testing"""
    
    test_texts = [
        "This is the first test audio file.",
        "Here is the second test audio for concatenation.",  
        "Third audio file for mixed concatenation testing.",
        "Fourth test file to ensure we have enough samples.",
        "Fifth and final test audio for comprehensive testing."
    ]
    
    print("Generating small test files...")
    
    for i, text in enumerate(test_texts, 1):
        print(f"Generating test file {i}/5...")
        
        tts_request = {
            "text": text,
            "export_formats": ["wav"],
            "temperature": 0.75,
            "seed": i * 100  # Different seed for each
        }
        
        try:
            response = requests.post(f"{API_BASE}/api/v1/tts", json=tts_request, timeout=60) #?response_mode=url
            
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print(f"  ✓ Generated test file {i} ({size_kb:.1f} KB)")
            else:
                print(f"  ✗ Failed to generate test file {i}: {response.status_code}")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Exception generating test file {i}: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\nTest file generation complete!")

if __name__ == "__main__":
    generate_test_files()

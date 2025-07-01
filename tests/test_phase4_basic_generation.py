#!/usr/bin/env python3
"""
Phase 4 Test: Basic TTS Generation (No Retry Needed)

Purpose: Validate basic TTS generation with bypass_whisper_checking=True
This test ensures the retry queue implementation doesn't break basic functionality.

Expected Results:
- Status: 200 (Success)
- Processing: Sequential (single chunk)
- Whisper: Bypassed
- Time: ~8-15 seconds
- Log Evidence: "Bypassing Whisper validation - selecting shortest duration candidates"
"""

import requests
import time
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_generation():
    """Test basic TTS generation without Whisper validation"""
    print("[TEST] Testing Basic TTS Generation (No Retry Needed)")
    print("=" * 60)
    
    # Test configuration
    test_data = {
        'text': 'Testing retry queue implementation.',
        'num_generations': 1,
        'num_candidates_per_chunk': 1,
        'max_attempts_per_candidate': 2,
        'bypass_whisper_checking': True  # Should bypass validation
    }
    
    print(f"[CONFIG] Test Text: '{test_data['text']}'")
    print(f"[CONFIG] Config: {test_data['num_candidates_per_chunk']} candidate/chunk, bypass_whisper=True")
    print()
    
    # Make request
    start_time = time.time()
    try:
        response = requests.post(
            'http://127.0.0.1:7860/api/v1/tts',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        # Validate response
        print(f"[RESULTS] Results:")
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("   [SUCCESS] Basic generation works")
            
            # Check for expected log patterns
            print()
            print("[LOGS] Expected Log Evidence:")
            print("   - 'Bypassing Whisper validation - selecting shortest duration candidates'")
            print("   - 'Processing 1 chunks sequentially'")
            print("   - 'Single chunk copied to: outputs\\...'")
            
            return True
        else:
            print(f"   [FAILED] Unexpected status code")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] ERROR after {elapsed:.1f}s: {e}")
        return False

def main():
    """Run the basic generation test"""
    print("[PHASE4] Phase 4 Test: Basic TTS Generation")
    print("[INFO] Validates retry queue doesn't break basic functionality")
    print()
    
    success = test_basic_generation()
    
    print()
    print("=" * 60)
    if success:
        print("[PASS] TEST PASSED: Basic generation functionality intact")
        print("[PASS] Retry queue implementation doesn't break existing features")
    else:
        print("[FAIL] TEST FAILED: Basic generation broken")
        print("[FAIL] Review implementation for regression issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

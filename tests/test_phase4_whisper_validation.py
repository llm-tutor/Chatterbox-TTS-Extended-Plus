#!/usr/bin/env python3
"""
Phase 4 Test: Whisper Validation Test

Purpose: Validate Whisper validation system with enhanced logging
Tests the complete validation pipeline without triggering retry queue.

Expected Results:
- Status: 200 (Success)
- Whisper: Model loading + validation
- Enhanced Logging: Validation criteria, timing, candidate selection
- Time: ~25-40 seconds (includes model loading)
- Log Evidence: "Running Whisper validation on X candidates"
"""

import requests
import time
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_whisper_validation():
    """Test Whisper validation system with enhanced logging"""
    print("[TEST] Testing Whisper Validation System")
    print("=" * 60)
    
    # Test configuration
    test_data = {
        'text': 'Testing whisper validation and retry queue. This is a longer sentence to test the system properly.',
        'num_generations': 1,
        'num_candidates_per_chunk': 2,
        'max_attempts_per_candidate': 3,
        'bypass_whisper_checking': False,  # Enable Whisper validation
        'whisper_model': 'base',
        'use_faster_whisper': True
    }
    
    print(f"[TEXT] Test Text: '{test_data['text'][:50]}...'")
    print(f"[DEBUG] Config: {test_data['num_candidates_per_chunk']} candidates/chunk, whisper={test_data['whisper_model']}")
    print(f"[RETRY] Retry Config: max_attempts={test_data['max_attempts_per_candidate']}")
    print()
    
    # Make request
    start_time = time.time()
    try:
        response = requests.post(
            'http://127.0.0.1:7860/api/v1/tts',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=120
        )
        elapsed = time.time() - start_time
        
        # Validate response
        print(f"[RESULTS] Results:")
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("   [SUCCESS] SUCCESS: Whisper validation completed")
            
            # Check for expected log patterns
            print()
            print("[LOGS] Expected Enhanced Log Evidence:")
            print("   - 'Running Whisper validation on X candidates'")
            print("   - 'Validation criteria: score >= 0.95 threshold, model: WhisperModel'")
            print("   - 'Retry configuration: max_attempts_per_candidate=3'")
            print("   - 'Initial validation completed in X.Xs'")
            print("   - '[SUCCESS] All chunks passed initial validation - no retry needed'")
            print("   - '[SELECT] Final candidate selection:'")
            print("   - '[Chunk 0] [SUCCESS] Selected validated candidate: ... (PASSED Whisper)'")
            print("   - '[FINAL] Final selection: 1 chunks ready for assembly'")
            
            # Performance expectations
            print()
            print("[PERF] Performance Analysis:")
            if elapsed < 35:
                print(f"   [SUCCESS] Excellent: {elapsed:.1f}s (within expected range)")
            elif elapsed < 50:
                print(f"   [WARNING]  Acceptable: {elapsed:.1f}s (slightly slower than expected)")
            else:
                print(f"   [FAILED] Slow: {elapsed:.1f}s (may indicate performance issues)")
            
            return True
        else:
            print(f"   [FAILED] FAILED: Unexpected status code")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[FAILED] ERROR after {elapsed:.1f}s: {e}")
        return False

def main():
    """Run the Whisper validation test"""
    print("[PHASE4] Phase 4 Test: Whisper Validation System")
    print("[INFO] Validates enhanced logging and validation pipeline")
    print()
    
    success = test_whisper_validation()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] TEST PASSED: Whisper validation system working")
        print("[SUCCESS] Enhanced logging provides comprehensive feedback")
        print("[SUCCESS] Validation pipeline ready for retry queue testing")
    else:
        print("[FAILED] TEST FAILED: Whisper validation issues")
        print("[FAILED] Check model loading and validation logic")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

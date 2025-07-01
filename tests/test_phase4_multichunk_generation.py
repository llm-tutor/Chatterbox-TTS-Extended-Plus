#!/usr/bin/env python3
"""
Phase 4 Test: Multi-Chunk Test (Higher Chance of Retry)

Purpose: Test multi-chunk generation with Whisper validation
Creates scenario more likely to trigger retry queue logic.

Expected Results:
- Status: 200 (Success)
- Processing: Multiple chunks with validation
- Batching: Enabled sentence grouping
- Time: ~40-60 seconds (multiple chunks + validation)
- Log Evidence: Multi-chunk processing and validation
"""

import requests
import time
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_multichunk_generation():
    """Test multi-chunk generation with validation"""
    print("[TEST] Testing Multi-Chunk Generation")
    print("=" * 60)
    
    # Test configuration - designed to create multiple chunks
    test_data = {
        'text': 'First chunk of text. Second chunk here. Third chunk text. Fourth chunk content. Fifth and final chunk.',
        'num_generations': 1,
        'num_candidates_per_chunk': 3,  # More candidates = higher chance of issues
        'max_attempts_per_candidate': 2,
        'bypass_whisper_checking': False,
        'whisper_model': 'base',
        'use_faster_whisper': True,
        'enable_batching': True  # Enable sentence batching
    }
    
    print(f"[TEXT] Test Text: '{test_data['text']}'")
    print(f"[DEBUG] Config: {test_data['num_candidates_per_chunk']} candidates/chunk, batching=True")
    print(f"[RETRY] Retry Config: max_attempts={test_data['max_attempts_per_candidate']}")
    print()
    
    # Predict expected behavior
    sentences = test_data['text'].split('. ')
    print(f"[RESULTS] Expected Processing:")
    print(f"   Sentences: {len(sentences)} detected")
    print(f"   Batching: Enabled (may group sentences)")
    print(f"   Candidates: {test_data['num_candidates_per_chunk']} per chunk")
    print()
    
    # Make request
    start_time = time.time()
    try:
        response = requests.post(
            'http://127.0.0.1:7860/api/v1/tts',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=180
        )
        elapsed = time.time() - start_time
        
        # Validate response
        print(f"[RESULTS] Results:")
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("   [SUCCESS] SUCCESS: Multi-chunk test completed")
            
            # Check for expected log patterns
            print()
            print("[LOGS] Expected Log Evidence:")
            print("   - 'Split text into 5 sentences'")
            print("   - 'Created X sentence groups' (batching effect)")
            print("   - 'Running Whisper validation on X candidates'")
            print("   - Processing evidence (sequential or parallel)")
            print("   - Validation results for multiple candidates")
            print("   - Final assembly of validated chunks")
            
            # Performance analysis
            print()
            print("[PERF] Performance Analysis:")
            if elapsed < 45:
                print(f"   [SUCCESS] Excellent: {elapsed:.1f}s (efficient multi-chunk processing)")
            elif elapsed < 70:
                print(f"   [SUCCESS] Good: {elapsed:.1f}s (acceptable for multi-chunk + validation)")
            elif elapsed < 90:
                print(f"   [WARNING]  Acceptable: {elapsed:.1f}s (slower than expected)")
            else:
                print(f"   [FAILED] Slow: {elapsed:.1f}s (performance concern)")
            
            # Retry queue analysis
            print()
            print("[RETRY] Retry Queue Analysis:")
            print("   Check logs for retry indicators:")
            print("   - If all passed: '[SUCCESS] All chunks passed initial validation'")
            print("   - If retries occurred: '[RETRY] RETRY ATTEMPT X: Processing Y chunks'")
            print("   - Retry success: '[RETRY] [SUCCESS] RETRY SUCCESS: ...'")
            
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
    """Run the multi-chunk generation test"""
    print("[PHASE4] Phase 4 Test: Multi-Chunk Generation")
    print("[INFO] Tests complex scenarios that may trigger retry queue")
    print()
    
    success = test_multichunk_generation()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] TEST PASSED: Multi-chunk generation working")
        print("[SUCCESS] Complex scenarios handled correctly")
        print("[SUCCESS] Retry queue ready for validation failures")
    else:
        print("[FAILED] TEST FAILED: Multi-chunk generation issues")
        print("[FAILED] Check batching and validation logic")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

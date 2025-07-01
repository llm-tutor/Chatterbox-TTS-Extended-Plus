#!/usr/bin/env python3
"""
Phase 4 Comprehensive Test Suite

Purpose: Run all Phase 4 tests in sequence for complete validation
Validates the entire Whisper validation system and retry queue implementation.

Test Sequence:
1. Basic Generation (bypass validation)
2. Whisper Validation (full pipeline)
3. Multi-Chunk Generation (complex scenarios)
4. Enhanced Logging (Task 4.6 validation)
5. Core Tests Integration

Expected Results:
- All tests pass: Phase 4 implementation complete
- Comprehensive logging: Enhanced visibility working
- Performance: Within acceptable ranges
- Backward compatibility: Core tests still pass
"""

import subprocess
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test(test_file, description):
    """Run a single test file and return success status"""
    print(f"[TEST] Running: {description}")
    print(f"[FILE] File: {test_file}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=project_root,
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[SUCCESS] PASSED: {description} ({elapsed:.1f}s)")
            return True
        else:
            print(f"[FAILED] FAILED: {description} ({elapsed:.1f}s)")
            return False
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"[TIMEOUT] TIMEOUT: {description} ({elapsed:.1f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] ERROR: {description} ({elapsed:.1f}s) - {e}")
        return False

def run_core_tests():
    """Run core validation tests"""
    print(f"[TEST] Running: Core Validation Tests")
    print(f"[FILE] File: scripts/test_core_examples.py")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "scripts/test_core_examples.py"],
            cwd=project_root,
            capture_output=False,
            text=True,
            timeout=300
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[SUCCESS] PASSED: Core Validation Tests ({elapsed:.1f}s)")
            return True
        else:
            print(f"[FAILED] FAILED: Core Validation Tests ({elapsed:.1f}s)")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] ERROR: Core Validation Tests ({elapsed:.1f}s) - {e}")
        return False

def main():
    """Run comprehensive Phase 4 test suite"""
    print("[PHASE4] Phase 4 Comprehensive Test Suite")
    print("[INFO] Complete validation of Whisper system and retry queue")
    print("=" * 80)
    print()
    
    # Test configuration
    tests = [
        ("tests/test_phase4_basic_generation.py", "Basic Generation (No Retry)"),
        ("tests/test_phase4_whisper_validation.py", "Whisper Validation System"),
        ("tests/test_phase4_multichunk_generation.py", "Multi-Chunk Generation"),
        ("tests/test_phase4_enhanced_logging.py", "Enhanced Logging Validation"),
    ]
    
    results = []
    total_start = time.time()
    
    # Run Phase 4 specific tests
    print("[RETRY] Phase 4 Specific Tests:")
    print()
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
        print()
    
    # Run core tests to ensure backward compatibility
    print("[RETRY] Backward Compatibility Tests:")
    print()
    core_success = run_core_tests()
    results.append(("Core Validation Tests", core_success))
    
    total_elapsed = time.time() - total_start
    
    # Summary
    print()
    print("=" * 80)
    print("[RESULTS] PHASE 4 TEST SUITE SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"⏱  Total Time: {total_elapsed:.1f}s")
    print(f"[STATS] Success Rate: {passed}/{total} ({100*passed/total:.1f}%)")
    print()
    
    print("[INFO] Individual Results:")
    for description, success in results:
        status = "[SUCCESS] PASS" if success else "[FAILED] FAIL"
        print(f"   {status}: {description}")
    
    print()
    
    # Overall assessment
    if passed == total:
        print("[COMPLETE] PHASE 4 COMPLETE!")
        print("[SUCCESS] All Whisper validation and retry queue features working")
        print("[SUCCESS] Enhanced logging provides comprehensive visibility")
        print("[SUCCESS] Backward compatibility maintained")
        print("[SUCCESS] Ready for Phase 5: Integration & Final Polish")
        
        print()
        print("[LOGS] Key Features Validated:")
        print("   [SUCCESS] Whisper model management (dual backend)")
        print("   [SUCCESS] Validation pipeline with fuzzy matching")
        print("   [SUCCESS] Full retry queue implementation")
        print("   [SUCCESS] Candidate selection strategies")
        print("   [SUCCESS] Enhanced logging with timing")
        print("   [SUCCESS] Performance within acceptable ranges")
        
        return True
    else:
        print("[FAILED] PHASE 4 INCOMPLETE")
        print(f"[FAILED] {total - passed} test(s) failed")
        print("[FAILED] Review failed tests before proceeding to Phase 5")
        
        print()
        print("[DEBUG] Troubleshooting Steps:")
        print("   1. Check server is running: http://127.0.0.1:7860/api/v1/health")
        print("   2. Review logs: logs/chatterbox_extended.log")
        print("   3. Verify model loading and VRAM availability")
        print("   4. Check network connectivity for model downloads")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

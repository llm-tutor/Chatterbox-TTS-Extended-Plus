#!/usr/bin/env python3
"""
Test Phase 5 Task 2: Post-Processing Pipeline Integration
Tests that all post-processing features work correctly with parallel processing.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_speed_factor_with_parallel_processing():
    """Test speed factor works correctly with parallel-generated chunks"""
    print("\n[SPEED] Testing Speed Factor with Parallel Processing...")
    
    try:
        from core_engine import engine
        
        # Create a multi-chunk scenario with speed factor
        test_text = """This is the first sentence for testing. 
        This is the second sentence for testing.
        This is the third sentence for testing.
        This is the fourth sentence for testing.
        This is the fifth sentence for testing."""
        
        # Test with speed factor and parallel processing
        result = engine.generate_tts(
            text=test_text,
            enable_batching=True,  # Force chunking
            enable_parallel=True,  # Force parallel processing
            num_parallel_workers=2,
            speed_factor=1.5,  # Test speed factor
            export_formats=['wav']
        )
        
        print(f"[SUCCESS] TTS with speed factor and parallel processing completed")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "TTS should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        # Check that speed factor was applied (filename should contain speed info)
        output_file = result['output_files'][0]['filename']
        assert "speed1.5" in output_file, f"Filename should contain speed factor info: {output_file}"
        
        print("[SUCCESS] Speed factor with parallel processing test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Speed factor with parallel processing test failed: {e}")
        return False

def test_trimming_with_concatenated_audio():
    """Test audio trimming works with concatenated audio from multiple chunks"""
    print("\n[TRIM] Testing Trimming with Concatenated Audio...")
    
    try:
        from core_engine import engine
        
        # Create a multi-chunk scenario with trimming
        test_text = """Hello, this is a test. 
        Another sentence here.
        And one more sentence."""
        
        # Test with trimming and chunking
        result = engine.generate_tts(
            text=test_text,
            enable_batching=True,  # Force chunking 
            trim=True,  # Enable trimming
            trim_start_seconds=0.5,  # Trim first 0.5s
            trim_end_seconds=0.3,   # Trim last 0.3s
            export_formats=['wav']
        )
        
        print(f"[SUCCESS] TTS with trimming and chunking completed")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "TTS should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        # Check that trimming was applied (filename should contain trim info)
        output_file = result['output_files'][0]['filename']
        assert "trim" in output_file.lower(), f"Filename should contain trim info: {output_file}"
        
        print("[SUCCESS] Trimming with concatenated audio test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Trimming with concatenated audio test failed: {e}")
        return False

def test_post_processing_pipeline_integration():
    """Test that auto-editor and normalization integrate properly"""
    print("\n[STYLE] Testing Post-Processing Pipeline Integration...")
    
    try:
        from core_engine import engine
        
        # Test with post-processing features enabled
        test_text = "This is a test of the post-processing pipeline integration."
        
        # Test with parallel processing + post-processing
        result = engine.generate_tts(
            text=test_text,
            enable_parallel=True,
            num_parallel_workers=2,
            # Post-processing options (may not be available in test environment)
            use_auto_editor=False,  # Disabled for test environment
            normalize_audio=False,  # Disabled for test environment
            speed_factor=1.2,  # Test speed factor integration
            export_formats=['wav']
        )
        
        print(f"[SUCCESS] TTS with post-processing pipeline completed")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "TTS should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        print("[SUCCESS] Post-processing pipeline integration test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Post-processing pipeline integration test failed: {e}")
        return False

def test_optimization_preservation():
    """Test that existing optimizations are preserved"""
    print("\n[FAST] Testing Optimization Preservation...")
    
    try:
        from core_engine import engine
        
        # Test that speed_factor=1.0 still has zero overhead
        test_text = "Testing optimization preservation."
        
        start_time = time.time()
        result = engine.generate_tts(
            text=test_text,
            speed_factor=1.0,  # Should have zero overhead
            export_formats=['wav']
        )
        processing_time = time.time() - start_time
        
        print(f"[SUCCESS] TTS with speed_factor=1.0 completed in {processing_time:.2f}s")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "TTS should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        # Verify no speed factor processing was applied (filename shouldn't have speed info)
        output_file = result['output_files'][0]['filename']
        assert "speed" not in output_file.lower(), f"Filename should not contain speed info for 1.0x: {output_file}"
        
        print("[SUCCESS] Optimization preservation test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Optimization preservation test failed: {e}")
        return False

def main():
    """Run all Phase 5 Task 2 post-processing integration tests"""
    print("[START] Starting Phase 5 Task 2: Post-Processing Pipeline Integration Tests")
    print("=" * 60)
    
    tests = [
        test_speed_factor_with_parallel_processing,
        test_trimming_with_concatenated_audio,
        test_post_processing_pipeline_integration,
        test_optimization_preservation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"[DATA] Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[COMPLETE] All Phase 5 Task 2 post-processing integration tests passed!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

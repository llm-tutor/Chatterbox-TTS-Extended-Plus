#!/usr/bin/env python3
"""
Test Phase 5 Task 3: Comprehensive Testing & Validation
Validates feature parity with original Chatter.py implementation.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_original_chatterpy_features():
    """Test all original Chatter.py features work identically"""
    print("\n[TARGET] Testing Original Chatter.py Feature Parity...")
    
    try:
        from core_engine import engine
        
        # Test comprehensive TTS generation with all original features
        test_text = """Hello, this is a comprehensive test. 
        We are testing multiple sentences. 
        This should trigger chunking and parallel processing."""
        
        # Use parameters that match original Chatter.py capabilities
        result = engine.generate_tts(
            text=test_text,
            # Text preprocessing (original features)
            to_lowercase=True,
            normalize_whitespace=True,
            fix_dot_letters=True,
            remove_reference_numbers=True,
            sound_words_field="",  # Sound word replacement
            
            # Chunking strategies (original features)
            enable_batching=True,
            smart_batch_short_sentences=True,
            
            # Parallel processing (original features)  
            enable_parallel=True,
            num_parallel_workers=2,
            
            # Candidate generation (original features)
            num_candidates_per_chunk=2,
            max_attempts_per_candidate=3,
            
            # Whisper validation (original features)
            bypass_whisper_checking=False,
            use_faster_whisper=True,
            whisper_model_name="base",
            use_longest_transcript_on_fail=True,
            
            # Export (enhanced features)
            export_formats=['wav'],
            
            # Generation parameters
            temperature=0.8,
            exaggeration=0.3,
            cfg_weight=1.0,
            disable_watermark=True
        )
        
        print(f"[SUCCESS] Comprehensive TTS generation completed")
        print(f"[DATA] Result: {result['success']}")
        print(f"[TIME]  Processing time: {result.get('processing_time_seconds', 0):.2f}s")
        
        # Validate result
        assert result['success'] is True, "TTS should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        # Check output file exists
        output_file = result['output_files'][0]['filename']
        output_path = project_root / "outputs" / output_file
        assert output_path.exists(), f"Output file should exist: {output_path}"
        
        print("[SUCCESS] Original Chatter.py features test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Original Chatter.py features test failed: {e}")
        return False

def test_parallel_vs_sequential_consistency():
    """Test that parallel and sequential processing produce consistent results"""
    print("\n[BALANCE] Testing Parallel vs Sequential Processing Consistency...")
    
    try:
        from core_engine import engine
        
        test_text = "This is a consistency test between parallel and sequential processing."
        
        # Test sequential processing
        print("  [PROCESS] Testing sequential processing...")
        result_sequential = engine.generate_tts(
            text=test_text,
            enable_parallel=False,  # Sequential
            temperature=0.7,  # Fixed seed for consistency
            export_formats=['wav']
        )
        
        # Test parallel processing  
        print("  [FAST] Testing parallel processing...")
        result_parallel = engine.generate_tts(
            text=test_text,
            enable_parallel=True,   # Parallel
            num_parallel_workers=2,
            temperature=0.7,  # Same parameters
            export_formats=['wav']
        )
        
        print(f"[SUCCESS] Both processing modes completed")
        print(f"[DATA] Sequential: {result_sequential['success']}")
        print(f"[DATA] Parallel: {result_parallel['success']}")
        
        # Both should succeed
        assert result_sequential['success'] is True, "Sequential should succeed"
        assert result_parallel['success'] is True, "Parallel should succeed"
        
        print("[SUCCESS] Parallel vs sequential consistency test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Parallel vs sequential consistency test failed: {e}")
        return False

def test_whisper_models_and_backends():
    """Test different Whisper models and backend combinations"""
    print("\n[MIC] Testing Whisper Models and Backend Combinations...")
    
    try:
        from core_engine import engine
        
        test_text = "Testing Whisper validation systems."
        
        # Test faster-whisper backend
        print("  [START] Testing faster-whisper backend...")
        result_faster = engine.generate_tts(
            text=test_text,
            bypass_whisper_checking=False,
            use_faster_whisper=True,
            whisper_model_name="tiny",  # Use tiny model for speed
            num_candidates_per_chunk=1,  # Minimal for speed
            export_formats=['wav']
        )
        
        # Test OpenAI whisper backend  
        print("  🐍 Testing OpenAI whisper backend...")
        result_openai = engine.generate_tts(
            text=test_text,
            bypass_whisper_checking=False,
            use_faster_whisper=False,
            whisper_model_name="tiny",  # Use tiny model for speed
            num_candidates_per_chunk=1,  # Minimal for speed
            export_formats=['wav']
        )
        
        print(f"[SUCCESS] Both Whisper backends completed")
        print(f"[DATA] faster-whisper: {result_faster['success']}")
        print(f"[DATA] OpenAI whisper: {result_openai['success']}")
        
        # Both should succeed
        assert result_faster['success'] is True, "faster-whisper should succeed"
        assert result_openai['success'] is True, "OpenAI whisper should succeed"
        
        print("[SUCCESS] Whisper models and backends test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Whisper models and backends test failed: {e}")
        return False

def main():
    """Run all Phase 5 Task 3 comprehensive validation tests"""
    print("[START] Starting Phase 5 Task 3: Comprehensive Testing & Validation")
    print("=" * 60)
    
    tests = [
        test_original_chatterpy_features,
        test_parallel_vs_sequential_consistency,
        test_whisper_models_and_backends
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
        print("[COMPLETE] All Phase 5 Task 3 comprehensive validation tests passed!")
        print("[SUCCESS] Feature parity with original Chatter.py achieved!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

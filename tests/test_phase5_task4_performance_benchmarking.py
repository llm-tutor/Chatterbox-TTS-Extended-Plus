#!/usr/bin/env python3
"""
Test Phase 5 Task 4: Performance Optimization & Benchmarking
Comparative performance testing against original Chatter.py patterns.
"""

import sys
import os
import time
import psutil
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class PerformanceMonitor:
    """Monitor system resources during test execution"""
    
    def __init__(self):
        self.monitoring = False
        self.max_memory_mb = 0
        self.avg_cpu_percent = 0
        self.samples = []
        
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        self.monitoring = True
        self.max_memory_mb = 0
        self.samples = []
        
        def monitor():
            process = psutil.Process()
            while self.monitoring:
                try:
                    # Memory usage
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    self.max_memory_mb = max(self.max_memory_mb, memory_mb)
                    
                    # CPU usage
                    cpu_percent = process.cpu_percent()
                    self.samples.append(cpu_percent)
                    
                    time.sleep(0.5)  # Sample every 500ms
                except:
                    break
                    
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring and return stats"""
        self.monitoring = False
        time.sleep(0.6)  # Wait for final sample
        
        self.avg_cpu_percent = sum(self.samples) / len(self.samples) if self.samples else 0
        
        return {
            'max_memory_mb': self.max_memory_mb,
            'avg_cpu_percent': self.avg_cpu_percent
        }

def test_single_chunk_performance():
    """Test performance with single chunk (baseline)"""
    print("\n[FAST] Testing Single Chunk Performance...")
    
    try:
        from core_engine import engine
        
        # Single sentence - should not trigger parallel processing
        test_text = "This is a single sentence performance test."
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        start_time = time.time()
        result = engine.generate_tts(
            text=test_text,
            enable_parallel=False,  # Sequential for baseline
            temperature=0.7,
            export_formats=['wav']
        )
        end_time = time.time()
        
        stats = monitor.stop_monitoring()
        processing_time = end_time - start_time
        
        print(f"[SUCCESS] Single chunk completed in {processing_time:.2f}s")
        print(f"[DATA] Memory: {stats['max_memory_mb']:.1f}MB")
        print(f"[DATA] CPU: {stats['avg_cpu_percent']:.1f}%")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "Single chunk should succeed"
        assert processing_time < 120, "Should complete within 2 minutes"
        
        print("[SUCCESS] Single chunk performance test passed!")
        return {
            'processing_time': processing_time,
            'memory_mb': stats['max_memory_mb'],
            'cpu_percent': stats['avg_cpu_percent']
        }
        
    except Exception as e:
        print(f"[ERROR] Single chunk performance test failed: {e}")
        return None

def test_parallel_processing_performance():
    """Test performance with parallel processing"""
    print("\n[START] Testing Parallel Processing Performance...")
    
    try:
        from core_engine import engine
        
        # Multi-sentence text - should trigger parallel processing
        test_text = """This is the first sentence for parallel testing.
        This is the second sentence for parallel testing.
        This is the third sentence for parallel testing.
        This is the fourth sentence for parallel testing.
        This is the fifth sentence for parallel testing."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        start_time = time.time()
        result = engine.generate_tts(
            text=test_text,
            enable_batching=True,        # Force chunking
            enable_parallel=True,        # Parallel processing
            num_parallel_workers=3,      # Multiple workers
            num_candidates_per_chunk=2,  # Multiple candidates
            temperature=0.7,
            export_formats=['wav']
        )
        end_time = time.time()
        
        stats = monitor.stop_monitoring()
        processing_time = end_time - start_time
        
        print(f"[SUCCESS] Parallel processing completed in {processing_time:.2f}s")
        print(f"[DATA] Memory: {stats['max_memory_mb']:.1f}MB")
        print(f"[DATA] CPU: {stats['avg_cpu_percent']:.1f}%")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "Parallel processing should succeed"
        assert processing_time < 300, "Should complete within 5 minutes"
        
        print("[SUCCESS] Parallel processing performance test passed!")
        return {
            'processing_time': processing_time,
            'memory_mb': stats['max_memory_mb'],
            'cpu_percent': stats['avg_cpu_percent']
        }
        
    except Exception as e:
        print(f"[ERROR] Parallel processing performance test failed: {e}")
        return None

def test_whisper_validation_performance():
    """Test performance with Whisper validation enabled"""
    print("\n[MIC] Testing Whisper Validation Performance...")
    
    try:
        from core_engine import engine
        
        # Multi-sentence text with Whisper validation
        test_text = """Testing Whisper validation performance. 
        This should process multiple candidates.
        And validate them with Whisper."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        start_time = time.time()
        result = engine.generate_tts(
            text=test_text,
            enable_batching=True,
            enable_parallel=True,
            num_parallel_workers=2,
            # Whisper validation settings
            bypass_whisper_checking=False,
            use_faster_whisper=True,      # Use faster backend
            whisper_model_name="tiny",    # Use smallest model for speed
            num_candidates_per_chunk=2,
            max_attempts_per_candidate=2,
            temperature=0.7,
            export_formats=['wav']
        )
        end_time = time.time()
        
        stats = monitor.stop_monitoring()
        processing_time = end_time - start_time
        
        print(f"[SUCCESS] Whisper validation completed in {processing_time:.2f}s")
        print(f"[DATA] Memory: {stats['max_memory_mb']:.1f}MB")
        print(f"[DATA] CPU: {stats['avg_cpu_percent']:.1f}%")
        print(f"[DATA] Result: {result['success']}")
        
        # Validate result
        assert result['success'] is True, "Whisper validation should succeed"
        assert processing_time < 400, "Should complete within 6.5 minutes"
        
        print("[SUCCESS] Whisper validation performance test passed!")
        return {
            'processing_time': processing_time,
            'memory_mb': stats['max_memory_mb'],
            'cpu_percent': stats['avg_cpu_percent']
        }
        
    except Exception as e:
        print(f"[ERROR] Whisper validation performance test failed: {e}")
        return None

def test_resource_usage_efficiency():
    """Test resource usage efficiency"""
    print("\n[DATA] Testing Resource Usage Efficiency...")
    
    try:
        from core_engine import engine
        
        # Test memory cleanup after generation
        initial_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        # Run multiple small generations
        for i in range(3):
            result = engine.generate_tts(
                text=f"Memory test iteration {i+1}.",
                temperature=0.7,
                export_formats=['wav']
            )
            assert result['success'] is True, f"Iteration {i+1} should succeed"
        
        # Check memory after generations
        final_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        memory_increase = final_memory - initial_memory
        
        print(f"[SUCCESS] Multiple generations completed")
        print(f"[DATA] Initial memory: {initial_memory:.1f}MB")
        print(f"[DATA] Final memory: {final_memory:.1f}MB")
        print(f"[DATA] Memory increase: {memory_increase:.1f}MB")
        
        # Memory increase should be reasonable (< 500MB for small tests)
        assert memory_increase < 500, f"Memory increase should be reasonable: {memory_increase:.1f}MB"
        
        print("[SUCCESS] Resource usage efficiency test passed!")
        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase
        }
        
    except Exception as e:
        print(f"[ERROR] Resource usage efficiency test failed: {e}")
        return None

def main():
    """Run all Phase 5 Task 4 performance optimization tests"""
    print("[START] Starting Phase 5 Task 4: Performance Optimization & Benchmarking")
    print("=" * 60)
    
    tests = [
        ('Single Chunk', test_single_chunk_performance),
        ('Parallel Processing', test_parallel_processing_performance),
        ('Whisper Validation', test_whisper_validation_performance),
        ('Resource Efficiency', test_resource_usage_efficiency)
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result is not None:
                results[test_name] = result
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] Test {test_name} crashed: {e}")
            failed += 1
    
    # Performance summary
    print("\n" + "=" * 60)
    print("[DATA] PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for test_name, stats in results.items():
        print(f"\n[ITEM] {test_name}:")
        for key, value in stats.items():
            if 'time' in key:
                print(f"  [TIME]  {key}: {value:.2f}s")
            elif 'memory' in key:
                print(f"  [MEMORY] {key}: {value:.1f}MB") 
            elif 'cpu' in key:
                print(f"  [CPU]  {key}: {value:.1f}%")
            else:
                print(f"  [DATA] {key}: {value}")
    
    print(f"\n[DATA] Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[COMPLETE] All Phase 5 Task 4 performance tests passed!")
        print("[SUCCESS] Performance optimization validated successfully!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

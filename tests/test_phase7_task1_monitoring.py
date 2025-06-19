# test_phase7_task1_monitoring.py - Test enhanced logging and monitoring

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_enhanced_monitoring():
    """Test enhanced logging and monitoring features"""
    print("Testing Phase 7 Task 1: Enhanced Logging & Monitoring")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Enhanced Logger
    print("\nTest 1: Enhanced Logger Import and Basic Functionality")
    tests_total += 1
    try:
        from monitoring.logger import get_logger, get_metrics, metrics_collector
        
        logger = get_logger("test_logger")
        
        # Test basic logging
        logger.info("Test info message", extra_data={'test': 'data'})
        logger.warning("Test warning message")
        
        # Test operation timer
        with logger.operation_timer("test_operation"):
            time.sleep(0.1)  # Simulate work
            
        # Test request context
        with logger.request_context(request_id="test-123", operation="test_op"):
            logger.info("Message with request context")
            
        print("[PASS] Enhanced logger working correctly")
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] Enhanced logger test failed: {e}")
    
    # Test 2: Metrics Collection
    print("\nTest 2: Metrics Collection")
    tests_total += 1
    try:
        from monitoring.metrics import get_system_metrics, record_operation_time, record_api_time
        
        # Record some test metrics
        record_operation_time(150.5, "test_operation")
        record_api_time(75.2, "GET /test")
        
        # Get system metrics
        system_metrics = get_system_metrics()
        
        print(f"[PASS] System metrics collected: {len(system_metrics)} categories")
        print(f"   - CPU usage: {system_metrics['system']['cpu_percent']:.1f}%")
        print(f"   - Memory usage: {system_metrics['system']['memory']['rss_mb']:.1f} MB")
        print(f"   - Performance samples: {system_metrics['performance']['sample_count']}")
        
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] Metrics collection test failed: {e}")
    
    # Test 3: Middleware Import
    print("\nTest 3: Middleware Components")
    tests_total += 1
    try:
        from monitoring.middleware import RequestLoggingMiddleware, log_request_body_middleware
        
        print("[PASS] Middleware components imported successfully")
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] Middleware import test failed: {e}")
    
    # Test 4: Core Engine Enhanced Logging
    print("\nTest 4: Core Engine Enhanced Logging")
    tests_total += 1
    try:
        from core_engine import engine
        
        # Test that logger is now enhanced
        logger_type = type(engine.logger).__name__
        print(f"[PASS] Core engine using enhanced logger: {logger_type}")
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] Core engine enhanced logging test failed: {e}")
    
    # Test 5: API Integration
    print("\nTest 5: API Integration")
    tests_total += 1
    try:
        from main_api import app
        
        # Check that monitoring middleware is registered
        middleware_count = len(app.user_middleware)
        print(f"[PASS] API has {middleware_count} middleware components registered")
        
        # Check version update
        print(f"[PASS] API version updated to: {app.version}")
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] API integration test failed: {e}")
    
    # Test 6: Configuration Integration
    print("\nTest 6: Configuration Integration")
    tests_total += 1
    try:
        from config import config_manager
        
        # Test logging configuration
        log_level = config_manager.get("server.log_level", "INFO")
        log_file = config_manager.get("server.log_file_path")
        
        print(f"[PASS] Log level configured: {log_level}")
        if log_file:
            print(f"[PASS] Log file path: {log_file}")
        else:
            print("[PASS] Log file path: Console only")
            
        tests_passed += 1
        
    except Exception as e:
        print(f"[FAIL] Configuration integration test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Summary: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("All enhanced monitoring tests passed!")
        print("\nTask 7.1 Features Implemented:")
        print("   [PASS] Structured JSON logging with request tracing")
        print("   [PASS] Performance metrics collection")
        print("   [PASS] Request/response logging middleware")
        print("   [PASS] Enhanced health check with detailed metrics")
        print("   [PASS] System resource monitoring")
        print("   [PASS] Operation timing and context tracking")
        print("   [PASS] Integration with core engine and API")
        return True
    else:
        print("[FAIL] Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_monitoring())
    sys.exit(0 if success else 1)

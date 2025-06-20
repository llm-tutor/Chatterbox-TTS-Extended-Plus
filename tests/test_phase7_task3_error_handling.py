# tests/test_phase7_task3_error_handling.py - Comprehensive error handling tests

import sys
import os
import time
import tempfile
import requests_mock
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_error_tracker_imports():
    """Test that error tracking modules import correctly"""
    try:
        from resilience import error_tracker, ErrorCategory, ErrorSeverity
        from resilience.error_tracker import ErrorRecord
        print("OK Error tracker imports working")
        return True
    except Exception as e:
        print(f"ERROR Error tracker import failed: {e}")
        return False

def test_retry_handler_imports():
    """Test that retry handler modules import correctly"""
    try:
        from resilience import retry_download, RetryConfig, advanced_retry_handler
        print("✅ Retry handler imports working")
        return True
    except Exception as e:
        print(f"❌ Retry handler import failed: {e}")
        return False

def test_error_categorization():
    """Test automatic error categorization"""
    try:
        from resilience import error_tracker, ErrorCategory
        
        # Test network error categorization
        network_error = Exception("Connection timeout occurred")
        category = error_tracker.categorize_error(network_error, "download_operation")
        assert category == ErrorCategory.TRANSIENT, f"Expected TRANSIENT, got {category}"
        
        # Test memory error categorization  
        memory_error = Exception("Out of memory error")
        category = error_tracker.categorize_error(memory_error, "generation_operation")
        assert category == ErrorCategory.RESOURCE, f"Expected RESOURCE, got {category}"
        
        # Test configuration error categorization
        config_error = Exception("File not found")
        category = error_tracker.categorize_error(config_error, "model_loading")
        assert category == ErrorCategory.CONFIGURATION, f"Expected CONFIGURATION, got {category}"
        
        print("✅ Error categorization working correctly")
        return True
    except Exception as e:
        print(f"❌ Error categorization failed: {e}")
        return False

def test_retry_logic():
    """Test retry logic with mock failures"""
    try:
        from resilience import retry_download
        
        # Test successful operation (no retry needed)
        @retry_download(max_retries=2, base_delay=0.1)
        def successful_operation():
            return "success"
        
        result = successful_operation()
        assert result == "success", "Successful operation should return success"
        
        # Test operation that fails then succeeds
        call_count = 0
        @retry_download(max_retries=2, base_delay=0.1)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            return "success_after_retry"
        
        call_count = 0
        result = fail_then_succeed()
        assert result == "success_after_retry", "Should succeed after retry"
        assert call_count == 2, f"Should be called twice, was called {call_count} times"
        
        print("✅ Retry logic working correctly")
        return True
    except Exception as e:
        print(f"❌ Retry logic test failed: {e}")
        return False

def test_download_retry_integration():
    """Test download retry integration with core engine"""
    try:
        from core_engine import CoreEngine
        
        # Create engine instance
        engine = CoreEngine()
        
        # Test with mock HTTP responses
        with requests_mock.Mocker() as m:
            # Mock successful download after one failure
            test_url = "https://example.com/test.wav"
            temp_file = Path(tempfile.mktemp(suffix=".wav"))
            
            # First call fails, second succeeds
            m.get(test_url, [
                {'status_code': 500, 'text': 'Server Error'},
                {'status_code': 200, 'content': b'fake_audio_data'}
            ])
            
            # This should succeed after retry
            engine._download_file_sync(test_url, temp_file)
            
            # Verify file was created
            assert temp_file.exists(), "Downloaded file should exist"
            assert temp_file.read_bytes() == b'fake_audio_data', "File content should match"
            
            # Cleanup
            temp_file.unlink()
        
        print("✅ Download retry integration working")
        return True
    except Exception as e:
        print(f"❌ Download retry integration failed: {e}")
        return False

def test_error_tracking_integration():
    """Test error tracking integration with core engine"""
    try:
        from resilience import error_tracker
        from core_engine import CoreEngine
        
        # Clear any existing errors
        error_tracker.errors.clear()
        
        engine = CoreEngine()
        
        # Test error recording during download failure
        with requests_mock.Mocker() as m:
            test_url = "https://example.com/nonexistent.wav"
            temp_file = Path(tempfile.mktemp(suffix=".wav"))
            
            # Mock permanent failure
            m.get(test_url, status_code=404, text='Not Found')
            
            try:
                engine._download_file_sync(test_url, temp_file)
                assert False, "Should have raised an exception"
            except Exception:
                pass  # Expected to fail
            
            # Check that error was recorded
            assert len(error_tracker.errors) > 0, "Error should have been recorded"
            recent_error = error_tracker.errors[-1]
            assert recent_error.operation == "file_download", "Operation should be file_download"
            
        print("✅ Error tracking integration working")
        return True
    except Exception as e:
        print(f"❌ Error tracking integration failed: {e}")
        return False

def test_config_integration():
    """Test configuration integration for error handling"""
    try:
        from config import config_manager
        
        # Test error handling configuration
        max_retries = config_manager.get("error_handling.download_retries.max_retries", 2)
        assert isinstance(max_retries, int), "max_retries should be an integer"
        assert max_retries >= 0, "max_retries should be non-negative"
        
        base_delay = config_manager.get("error_handling.download_retries.base_delay_seconds", 2.0)
        assert isinstance(base_delay, (int, float)), "base_delay should be numeric"
        assert base_delay > 0, "base_delay should be positive"
        
        loading_timeout = config_manager.get("error_handling.model_loading.loading_timeout_seconds", 300)
        assert isinstance(loading_timeout, int), "loading_timeout should be an integer"
        assert loading_timeout >= 0, "loading_timeout should be non-negative"
        
        print("✅ Error handling configuration accessible")
        return True
    except Exception as e:
        print(f"❌ Configuration integration failed: {e}")
        return False

def test_api_error_endpoints():
    """Test API error tracking endpoints"""
    try:
        # This is a basic import test since we can't easily test API endpoints without starting the server
        from main_api import app
        from api_models import ErrorSummaryResponse
        
        # Verify error summary response model
        test_summary = ErrorSummaryResponse(
            total_errors=5,
            by_category={"transient": 3, "permanent": 2},
            by_severity={"medium": 4, "high": 1},
            by_operation={"download": 3, "generation": 2},
            most_frequent={"download:ConnectionError": 3},
            unresolved_count=1,
            recent_errors=[]
        )
        
        assert test_summary.total_errors == 5, "Summary model should work correctly"
        
        print("✅ API error endpoints accessible")
        return True
    except Exception as e:
        print(f"❌ API error endpoints test failed: {e}")
        return False

def main():
    """Run all error handling tests"""
    print("Running Phase 7 Task 7.3 Error Handling Tests...")
    print("=" * 60)
    
    tests = [
        ("Error Tracker Imports", test_error_tracker_imports),
        ("Retry Handler Imports", test_retry_handler_imports),
        ("Error Categorization", test_error_categorization),
        ("Retry Logic", test_retry_logic),
        ("Download Retry Integration", test_download_retry_integration),
        ("Error Tracking Integration", test_error_tracking_integration),
        ("Configuration Integration", test_config_integration),
        ("API Error Endpoints", test_api_error_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"X {test_name} failed")
        except Exception as e:
            print(f"X {test_name} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All error handling tests passed! Phase 7.3 implementation successful.")
        return True
    else:
        print(f"Warning: {total - passed} tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    main()

# Simple test for error handling basic functionality
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test basic imports work"""
    print("Testing basic imports...")
    
    try:
        from resilience import error_tracker, ErrorCategory, ErrorSeverity
        from resilience import retry_download, RetryConfig
        print("OK: Resilience module imports working")
        
        from config import config_manager
        print("OK: Config manager working")
        
        # Test configuration access
        max_retries = config_manager.get("error_handling.download_retries.max_retries", 2)
        print(f"OK: Config access working, max_retries = {max_retries}")
        
        return True
    except Exception as e:
        print(f"ERROR: Import failed - {e}")
        return False

def test_error_categorization():
    """Test error categorization"""
    print("Testing error categorization...")
    
    try:
        from resilience import error_tracker, ErrorCategory
        
        # Test network error
        network_error = Exception("Connection timeout")
        category = error_tracker.categorize_error(network_error, "download_operation")
        assert category == ErrorCategory.TRANSIENT
        print("OK: Network error categorized as TRANSIENT")
        
        # Test memory error
        memory_error = Exception("Out of memory")
        category = error_tracker.categorize_error(memory_error, "generation")
        assert category == ErrorCategory.RESOURCE
        print("OK: Memory error categorized as RESOURCE")
        
        return True
    except Exception as e:
        print(f"ERROR: Categorization failed - {e}")
        return False

def test_retry_decorator():
    """Test retry decorator basic functionality"""
    print("Testing retry decorator...")
    
    try:
        from resilience import retry_download
        
        @retry_download(max_retries=2, base_delay=0.1)
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
        print("OK: Retry decorator working")
        
        return True
    except Exception as e:
        print(f"ERROR: Retry decorator failed - {e}")
        return False

def main():
    """Run basic tests"""
    print("Phase 7.3 Error Handling - Basic Tests")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_error_categorization, 
        test_retry_decorator
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"Test crashed: {e}")
            print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("SUCCESS: Basic error handling implementation working!")
    else:
        print("WARNING: Some tests failed")

if __name__ == "__main__":
    main()

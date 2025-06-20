# tests/test_phase7_task2_resource_management.py - Phase 7.2 Resource Management Tests

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_file(path: Path, size_bytes: int = 1024):
    """Create a test file with specified size"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * size_bytes)
    return path

def create_old_file(path: Path, age_days: int = 2, size_bytes: int = 1024):
    """Create a test file and set its modification time to be old"""
    file_path = create_test_file(path, size_bytes)
    # Set modification time to be old
    old_time = time.time() - (age_days * 24 * 60 * 60)
    os.utime(file_path, (old_time, old_time))
    return file_path

def test_resource_manager_import():
    """Test that resource manager can be imported"""
    try:
        from management.resource_manager import ResourceManager, resource_manager
        print("[PASS] ResourceManager import successful")
        return True
    except Exception as e:
        print(f"[FAIL] ResourceManager import failed: {e}")
        return False

def test_cleanup_scheduler_import():
    """Test that cleanup scheduler can be imported"""
    try:
        from management.cleanup_scheduler import CleanupScheduler, cleanup_scheduler
        print("[PASS] CleanupScheduler import successful")
        return True
    except Exception as e:
        print(f"[FAIL] CleanupScheduler import failed: {e}")
        return False

def test_config_integration():
    """Test that resource management config is loaded correctly"""
    try:
        from config import config_manager
        
        # Check if resource management config exists
        cleanup_config = config_manager.get("resource_management.cleanup", {})
        
        if cleanup_config:
            print("[PASS] Resource management configuration loaded successfully")
            print(f"   Output dir max size: {cleanup_config.get('output_dir_max_size_gb', 'not set')}GB")
            print(f"   Temp dir max files: {cleanup_config.get('temp_dir_max_files', 'not set')}")
            print(f"   Cleanup on startup: {cleanup_config.get('cleanup_on_startup', 'not set')}")
            return True
        else:
            print("[FAIL] Resource management configuration not found")
            return False
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        return False

def test_resource_manager_functionality():
    """Test basic resource manager functionality"""
    try:
        from management.resource_manager import ResourceManager
        
        # Create a test resource manager
        manager = ResourceManager()
        
        # Test directory size calculation with empty directory
        temp_dir = Path(tempfile.mkdtemp())
        try:
            size = manager.get_directory_size(temp_dir)
            assert size == 0, f"Expected 0 bytes for empty dir, got {size}"
            
            # Create a test file and check size
            test_file = create_test_file(temp_dir / "test.wav", 1000)
            size = manager.get_directory_size(temp_dir)
            assert size == 1000, f"Expected 1000 bytes, got {size}"
            
            # Test file count
            count = manager.get_directory_file_count(temp_dir)
            assert count == 1, f"Expected 1 file, got {count}"
            
            print("[PASS] ResourceManager basic functionality working")
            return True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"[FAIL] ResourceManager functionality test failed: {e}")
        return False

def test_cleanup_scheduler_functionality():
    """Test basic cleanup scheduler functionality"""
    try:
        from management.cleanup_scheduler import CleanupScheduler
        
        # Create a test scheduler (don't start it)
        scheduler = CleanupScheduler()
        scheduler.cleanup_on_startup = False
        scheduler.cleanup_interval_hours = 0
        
        # Test status
        status = scheduler.get_status()
        assert "running" in status
        assert "cleanup_interval_hours" in status
        
        # Test force cleanup (this should work even if scheduler not running)
        result = scheduler.force_cleanup()
        assert "total_files_removed" in result
        assert "total_bytes_freed" in result
        
        print("[PASS] CleanupScheduler basic functionality working")
        return True
        
    except Exception as e:
        print(f"[FAIL] CleanupScheduler functionality test failed: {e}")
        return False

def test_api_integration():
    """Test that main_api can import the resource management modules"""
    try:
        # This will test if the imports in main_api.py work
        from management import cleanup_scheduler, resource_manager
        
        # Test that global instances are available
        assert cleanup_scheduler is not None
        assert resource_manager is not None
        
        print("[PASS] API integration imports working")
        return True
        
    except Exception as e:
        print(f"[FAIL] API integration test failed: {e}")
        return False

def test_enhanced_health_endpoint():
    """Test that the enhanced health endpoint with resource status works"""
    try:
        from management.resource_manager import resource_manager
        
        # Test getting resource status
        status = resource_manager.get_resource_status()
        
        # Verify expected structure
        assert "directories" in status
        assert "warnings" in status
        assert "timestamp" in status
        
        directories = status["directories"]
        for dir_name in ["outputs", "temp", "vc_inputs"]:
            assert dir_name in directories
            dir_info = directories[dir_name]
            assert "size_bytes" in dir_info
            assert "file_count" in dir_info
            assert "usage_percent" in dir_info
        
        print("[PASS] Enhanced health endpoint resource status working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Enhanced health endpoint test failed: {e}")
        return False

def run_all_tests():
    """Run all Phase 7.2 resource management tests"""
    print("=== Phase 7.2: Basic Resource Management Tests ===\n")
    
    tests = [
        ("Resource Manager Import", test_resource_manager_import),
        ("Cleanup Scheduler Import", test_cleanup_scheduler_import),
        ("Configuration Integration", test_config_integration),
        ("Resource Manager Functionality", test_resource_manager_functionality),
        ("Cleanup Scheduler Functionality", test_cleanup_scheduler_functionality),
        ("API Integration", test_api_integration),
        ("Enhanced Health Endpoint", test_enhanced_health_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_name} failed with exception: {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("SUCCESS: All Phase 7.2 tests passed!")
        return True
    else:
        print("WARNING: Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

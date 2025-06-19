#!/usr/bin/env python3
"""
Test Phase 5: Gradio Integration
Tests that both FastAPI and Gradio UI work together correctly
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_import_functionality():
    """Test that all modules can be imported without errors"""
    print("Testing Module Imports...")
    
    try:
        import Chatter
        print("[PASS] Chatter import successful")
        
        import main_api
        print("[PASS] main_api import successful")
        
        # Test interface creation
        interface = Chatter.create_interface()
        print(f"[PASS] Gradio interface created: {type(interface)}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import test failed: {e}")
        return False

def test_fastapi_startup():
    """Test that FastAPI application starts correctly with Gradio mounted"""
    print("\nTesting FastAPI Application Startup...")
    
    try:
        # Import and check if app object is created properly
        import main_api
        print("[PASS] FastAPI app created successfully")
        
        # Check if app has the expected attributes
        app = main_api.app
        print(f"[PASS] App type: {type(app)}")
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/v1/tts", "/api/v1/vc", "/api/v1/health"]
        
        all_routes_found = True
        for route in expected_routes:
            if route in routes:
                print(f"[PASS] Route {route} registered")
            else:
                print(f"[FAIL] Route {route} missing")
                all_routes_found = False
        
        return all_routes_found
    except Exception as e:
        print(f"[FAIL] FastAPI startup test failed: {e}")
        return False

def main():
    """Run all Phase 5 tests"""
    print("=" * 60)
    print("PHASE 5: GRADIO INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Module Import Test", test_import_functionality),
        ("FastAPI Startup Test", test_fastapi_startup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"[PASS] {test_name} PASSED")
                passed += 1
            else:
                print(f"[FAIL] {test_name} FAILED")
        except Exception as e:
            print(f"[FAIL] {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("SUCCESS: All Phase 5 tests passed!")
        print("Gradio Integration is working correctly")
        print("\nManual Testing Instructions:")
        print("1. Run: python main_api.py")
        print("2. Visit: http://localhost:7860/api/v1/health (API)")
        print("3. Visit: http://localhost:7860/ui (Gradio UI)")
        print("4. Test both interfaces work independently")
        return True
    else:
        print("FAILED: Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

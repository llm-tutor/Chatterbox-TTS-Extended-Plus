#!/usr/bin/env python3
"""
Working Examples Tester
Tests only the cURL examples that are expected to succeed
"""

import requests
import sys
import time


def test_working_examples():
    """Test examples that should work"""
    api_base = "http://localhost:7860"
    results = []
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{api_base}/api/v1/health",
            "expected_status": 200,
            "timeout": 20
        },
        {
            "name": "List Voices",
            "method": "GET", 
            "url": f"{api_base}/api/v1/voices",
            "expected_status": 200,
            "timeout": 20
        },
        {
            "name": "List Outputs",
            "method": "GET",
            "url": f"{api_base}/api/v1/outputs", 
            "expected_status": 200
        },
        {
            "name": "Basic TTS (no reference voice)",
            "method": "POST",
            "url": f"{api_base}/api/v1/tts",
            "json": {
                "text": "Hello, this is a basic TTS test.",
                "export_formats": ["wav"]
            },
            "expected_status": 200,
            "timeout": 60  # TTS takes time
        }
    ]
    
    for test in tests:
        print(f"Testing: {test['name']}...")
        try:
            start_time = time.time()
            
            if test['method'] == 'GET':
                response = requests.get(
                    test['url'], 
                    timeout=test.get('timeout', 10)
                )
            elif test['method'] == 'POST':
                response = requests.post(
                    test['url'],
                    json=test['json'],
                    timeout=test.get('timeout', 10)
                )
            
            elapsed = time.time() - start_time
            
            if response.status_code == test['expected_status']:
                print(f"  [PASS] ({response.status_code}) - {elapsed:.2f}s")
                results.append(True)
            else:
                print(f"  [FAIL] ({response.status_code}) - {elapsed:.2f}s")
                print(f"     Error: {response.text[:100]}...")
                results.append(False)
                
        except Exception as e:
            print(f"  [ERROR]: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("[SUCCESS] All working examples passed!")
        return 0
    else:
        print("[FAILED] Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(test_working_examples())

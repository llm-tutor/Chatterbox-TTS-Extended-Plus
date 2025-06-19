# test_performance_fix.py - Test script to validate performance improvements

import time
import requests
import json

def test_tts_performance():
    """Test TTS performance with the synchronous engine"""
    
    # Test data
    test_text = "Hello, this is a performance test of the synchronous TTS engine. We expect this to be much faster than the async version."
    
    url = "http://127.0.0.1:7860/api/v1/tts"
    payload = {
        "text": test_text,
        "export_formats": ["wav"]
    }
    
    print("=" * 60)
    print("PERFORMANCE TEST: Synchronous TTS Engine")
    print("=" * 60)
    print(f"Test text: {test_text}")
    print(f"URL: {url}")
    print()
    
    # Record start time
    start_time = time.time()
    print(f"Starting request at: {time.strftime('%H:%M:%S', time.localtime(start_time))}")
    
    try:
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"Request completed at: {time.strftime('%H:%M:%S', time.localtime(end_time))}")
        print(f"Total duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'No message')}")
            print(f"Output files: {len(result.get('output_files', []))}")
            print(f"Generation seed: {result.get('generation_seed_used', 'Unknown')}")
            
            if duration < 120:  # Less than 2 minutes
                print("✅ PERFORMANCE GOOD: Generation completed in under 2 minutes")
            elif duration < 300:  # Less than 5 minutes
                print("⚠️  PERFORMANCE FAIR: Generation took 2-5 minutes")
            else:
                print("❌ PERFORMANCE POOR: Generation took over 5 minutes")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Request failed with error: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    print("Make sure the server is running with: python main_api_sync.py")
    print("Press Enter to start the test...")
    input()
    test_tts_performance()

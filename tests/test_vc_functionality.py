# test_vc_functionality.py - Quick test to verify VC method works

import time
import requests
import json

def test_vc_api():
    """Test VC API functionality"""
    
    url = "http://127.0.0.1:7860/api/v1/vc"
    payload = {
        "input_audio_source": "test_input.wav",  # You'll need to have a test file
        "target_voice_source": "test_target.wav",  # You'll need to have a test file
        "export_formats": ["wav"]
    }
    
    print("=" * 60)
    print("TESTING: Voice Conversion API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ VC API Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    print("Make sure the server is running with: python main_api.py")
    print("And that you have test audio files in the appropriate directories")
    print("Press Enter to start the test...")
    input()
    test_vc_api()

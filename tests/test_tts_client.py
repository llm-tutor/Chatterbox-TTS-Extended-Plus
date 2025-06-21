#!/usr/bin/env python3
"""
TTS Test Client - Phase 9 Enhanced Features
Tests streaming responses, format selection, and enhanced naming
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

class TTSTestClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.media_dir = Path(__file__).parent / "media"
        self.media_dir.mkdir(exist_ok=True)
        
    def test_tts_streaming(
        self,
        text: str = "Hello world! This is a test of the enhanced TTS API with streaming responses.",
        reference_audio_filename: Optional[str] = None,
        export_formats: List[str] = ["wav", "mp3"],
        return_format: Optional[str] = None,
        response_mode: str = "stream",
        # TTS Parameters
        temperature: float = 0.75,
        seed: int = 42,
        exaggeration: float = 0.5,
        cfg_weight: float = 1.0,
        num_candidates_per_chunk: int = 3,
        max_attempts_per_candidate: int = 3,
        bypass_whisper_checking: bool = False,
        whisper_model_name: str = "medium",
        use_faster_whisper: bool = True,
        enable_batching: bool = False,
        # Audio processing
        normalize_audio: bool = False,
        normalize_method: str = "ebu",
        normalize_level: float = -24.0
    ):
        """Test TTS with streaming response and format selection"""
        
        # Prepare request payload
        payload = {
            "text": text,
            "export_formats": export_formats,
            "temperature": temperature,
            "seed": seed,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "num_candidates_per_chunk": num_candidates_per_chunk,
            "max_attempts_per_candidate": max_attempts_per_candidate,
            "bypass_whisper_checking": bypass_whisper_checking,
            "whisper_model_name": whisper_model_name,
            "use_faster_whisper": use_faster_whisper,
            "enable_batching": enable_batching,
            "normalize_audio": normalize_audio,
            "normalize_method": normalize_method,
            "normalize_level": normalize_level
        }
        
        if reference_audio_filename:
            payload["reference_audio_filename"] = reference_audio_filename
        
        # Prepare query parameters
        params = {"response_mode": response_mode}
        if return_format:
            params["return_format"] = return_format
        
        print(f"\n🎤 Testing TTS Generation")
        print(f"📝 Text: {text[:50]}...")
        print(f"🎵 Reference: {reference_audio_filename or 'None'}")
        print(f"📁 Formats: {export_formats}")
        print(f"🎯 Return format: {return_format or 'auto'}")
        print(f"📡 Response mode: {response_mode}")
        print(f"🌡️ Temperature: {temperature}, 🎲 Seed: {seed}")
        
        try:
            start_time = time.time()
            
            if response_mode == "stream":
                # Test streaming response
                response = requests.post(
                    f"{self.base_url}/api/v1/tts",
                    params=params,
                    json=payload,
                    stream=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    # Determine output filename
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"')
                    else:
                        # Generate filename based on parameters
                        timestamp = int(time.time())
                        fmt = return_format or export_formats[0]
                        filename = f"tts_test_{timestamp}_temp{temperature}_seed{seed}.{fmt}"
                    
                    output_path = self.media_dir / filename
                    
                    # Download file
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    elapsed = time.time() - start_time
                    file_size = output_path.stat().st_size
                    
                    print(f"✅ Success! Downloaded: {filename}")
                    print(f"📁 Saved to: {output_path}")
                    print(f"📊 File size: {file_size:,} bytes")
                    print(f"⏱️ Time: {elapsed:.2f}s")
                    
                    # Check for alternative formats in headers
                    alt_formats = response.headers.get('X-Alternative-Formats')
                    if alt_formats:
                        print(f"🔗 Alternative formats: {alt_formats}")
                    
                    return {
                        "success": True,
                        "filename": filename,
                        "path": str(output_path),
                        "size_bytes": file_size,
                        "elapsed_seconds": elapsed,
                        "alternative_formats": alt_formats
                    }
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"❌ Error {response.status_code}: {error_data}")
                    return {"success": False, "error": error_data, "status_code": response.status_code}
                    
            else:
                # Test JSON response
                response = requests.post(
                    f"{self.base_url}/api/v1/tts",
                    params=params,
                    json=payload,
                    timeout=300
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success! Generated {len(result.get('output_files', []))} files")
                    print(f"⏱️ Generation time: {result.get('processing_time_seconds', 0):.2f}s")
                    print(f"🎲 Seed used: {result.get('generation_seed_used')}")
                    
                    for file_info in result.get('output_files', []):
                        print(f"  📁 {file_info['format']}: {file_info['filename']}")
                        print(f"     🔗 URL: {file_info['url']}")
                    
                    return {
                        "success": True,
                        "result": result,
                        "elapsed_seconds": elapsed
                    }
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"❌ Error {response.status_code}: {error_data}")
                    return {"success": False, "error": error_data, "status_code": response.status_code}
                    
        except requests.exceptions.Timeout:
            print("⏰ Request timed out after 5 minutes")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Run TTS tests with different configurations"""
    client = TTSTestClient()
    
    print("🚀 Starting TTS Enhanced Features Test Suite")
    
    # Test 1: Basic streaming (default WAV)
    print("\n" + "="*60)
    print("TEST 1: Basic Streaming (WAV)")
    client.test_tts_streaming(
        text="This is test one with basic streaming response.",
        export_formats=["wav"],
        response_mode="stream"
    )
    
    # Test 2: Multi-format with MP3 streaming
    print("\n" + "="*60)
    print("TEST 2: Multi-format with MP3 Streaming")
    client.test_tts_streaming(
        text="This is test two requesting MP3 format specifically.",
        export_formats=["wav", "mp3", "flac"],
        return_format="mp3",
        response_mode="stream"
    )
    
    # Test 3: JSON response mode
    print("\n" + "="*60)
    print("TEST 3: JSON Response Mode")
    client.test_tts_streaming(
        text="This is test three using JSON response mode.",
        export_formats=["wav", "mp3"],
        response_mode="url"
    )
    
    # Test 4: With reference audio (placeholder)
    print("\n" + "="*60)
    print("TEST 4: With Reference Audio")
    client.test_tts_streaming(
        text="This is test four with reference audio cloning.",
        reference_audio_filename="speaker_en/jamie_vc_to_david-2.wav",  # Adjust this path as needed
        export_formats=["wav", "mp3"],
        return_format="wav",
        temperature=0.8,
        exaggeration=0.7
    )
    
    # Test 5: Enhanced parameters
    print("\n" + "="*60)
    print("TEST 5: Enhanced Parameters")
    client.test_tts_streaming(
        text="This is test five with enhanced parameters and settings.",
        export_formats=["wav", "mp3", "flac"],
        return_format="flac",
        temperature=0.9,
        seed=123,
        exaggeration=0.3,
        cfg_weight=1.2,
        normalize_audio=True
    )
    
    print("\n🎉 TTS Test Suite Complete!")
    print(f"📁 Check output files in: {client.media_dir}")

if __name__ == "__main__":
    main()

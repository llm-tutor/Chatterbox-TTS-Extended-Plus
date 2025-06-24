#!/usr/bin/env python3
"""
Voice Conversion Test Client - Phase 9 Enhanced Features  
Tests file upload, streaming responses, and format selection
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

class VCTestClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.media_dir = Path(__file__).parent / "media"
        self.media_dir.mkdir(exist_ok=True)
        
    def test_vc_json_mode(
        self,
        input_audio_source: str = "input_recording.wav",  # Placeholder - update with actual file
        target_voice_source: str = "speaker_en/DAVID-2.mp3",
        export_formats: List[str] = ["wav", "mp3"],
        return_format: Optional[str] = None,
        response_mode: str = "stream",
        # VC Parameters
        chunk_sec: int = 60,
        overlap_sec: float = 0.1,
        disable_watermark: bool = True
    ):
        """Test VC with JSON request (traditional mode)"""
        
        payload = {
            "input_audio_source": input_audio_source,
            "target_voice_source": target_voice_source,
            "chunk_sec": chunk_sec,
            "overlap_sec": overlap_sec,
            "disable_watermark": disable_watermark,
            "export_formats": export_formats
        }
        
        params = {"response_mode": response_mode}
        if return_format:
            params["return_format"] = return_format
        
        print(f"\n🎙️ Testing VC (JSON Mode)")
        print(f"📂 Input: {input_audio_source}")
        print(f"🎯 Target: {target_voice_source}")
        print(f"📁 Formats: {export_formats}")
        print(f"🎵 Return format: {return_format or 'auto'}")
        print(f"📡 Response mode: {response_mode}")
        print(f"⚙️ Chunk: {chunk_sec}s, Overlap: {overlap_sec}s")
        
        try:
            start_time = time.time()
            
            if response_mode == "stream":
                # Test streaming response
                response = requests.post(
                    f"{self.base_url}/api/v1/vc",
                    params=params,
                    json=payload,
                    stream=True,
                    timeout=600  # 10 minutes for VC
                )
                
                if response.status_code == 200:
                    # Determine output filename
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"')
                    else:
                        timestamp = int(time.time())
                        fmt = return_format or export_formats[0]
                        filename = f"vc_json_test_{timestamp}_chunk{chunk_sec}.{fmt}"
                    
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
                    
                    # Check for alternative formats
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
                    f"{self.base_url}/api/v1/vc",
                    params=params,
                    json=payload,
                    timeout=600
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success! Generated {len(result.get('output_files', []))} files")
                    print(f"⏱️ Processing time: {result.get('processing_time_seconds', 0):.2f}s")
                    
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
            print("⏰ Request timed out after 10 minutes")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_vc_file_upload(
        self,
        input_audio_file: str = "input_recording.wav",  # Placeholder - update with actual file
        target_voice_source: str = "speaker_en/DAVID-2.mp3",
        export_formats: str = "wav,mp3",
        return_format: Optional[str] = None,
        response_mode: str = "stream",
        # VC Parameters
        chunk_sec: int = 60,
        overlap_sec: float = 0.1,
        disable_watermark: bool = True
    ):
        """Test VC with direct file upload (new Phase 9 feature)"""
        
        input_path = self.media_dir / input_audio_file
        
        if not input_path.exists():
            print(f"❌ Input file not found: {input_path}")
            print(f"📝 Please copy your test audio file to: {input_path}")
            return {"success": False, "error": "input_file_not_found", "path": str(input_path)}
        
        params = {"response_mode": response_mode}
        if return_format:
            params["return_format"] = return_format
        
        # Prepare form data
        form_data = {
            'target_voice_source': target_voice_source,
            'chunk_sec': chunk_sec,
            'overlap_sec': overlap_sec,
            'disable_watermark': disable_watermark,
            'export_formats': export_formats
        }
        
        print(f"\n📤 Testing VC (File Upload Mode)")
        print(f"📂 Input file: {input_audio_file}")
        print(f"📊 File size: {input_path.stat().st_size:,} bytes")
        print(f"🎯 Target: {target_voice_source}")
        print(f"📁 Formats: {export_formats}")
        print(f"🎵 Return format: {return_format or 'auto'}")
        print(f"📡 Response mode: {response_mode}")
        print(f"⚙️ Chunk: {chunk_sec}s, Overlap: {overlap_sec}s")
        
        try:
            start_time = time.time()
            
            with open(input_path, 'rb') as audio_file:
                files = {'input_audio': (input_audio_file, audio_file, 'audio/wav')}
                
                if response_mode == "stream":
                    # Test streaming response with file upload
                    response = requests.post(
                        f"{self.base_url}/api/v1/vc",
                        params=params,
                        files=files,
                        data=form_data,
                        stream=True,
                        timeout=600  # 10 minutes for VC
                    )
                    
                    if response.status_code == 200:
                        # Determine output filename
                        content_disposition = response.headers.get('Content-Disposition', '')
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"')
                        else:
                            timestamp = int(time.time())
                            fmt = return_format or export_formats.split(',')[0]
                            filename = f"vc_upload_test_{timestamp}_chunk{chunk_sec}.{fmt}"
                        
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
                        
                        # Check for alternative formats
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
                    # Test JSON response with file upload
                    response = requests.post(
                        f"{self.base_url}/api/v1/vc",
                        params=params,
                        files=files,
                        data=form_data,
                        timeout=600
                    )
                    
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Success! Generated {len(result.get('output_files', []))} files")
                        print(f"⏱️ Processing time: {result.get('processing_time_seconds', 0):.2f}s")
                        
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
            print("⏰ Request timed out after 10 minutes")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Run VC tests with different configurations"""
    client = VCTestClient()
    
    print("🚀 Starting VC Enhanced Features Test Suite")
    
    # Test 1: JSON mode streaming (traditional) - No file is uploaded
    print("\n" + "="*60)
    print("TEST 1: JSON Mode Streaming (Traditional)")
    client.test_vc_json_mode(
        input_audio_source="josh.mp3",  # Update this filename - This file needs to exist in 'vc_inputs/'
        target_voice_source="speaker_en/DAVID-2.mp3",
        export_formats=["wav"],
        response_mode="stream"
    )

    # Test 2: JSON mode with format selection - No file is uploaded
    print("\n" + "="*60)
    print("TEST 2: JSON Mode with MP3 Return Format")
    client.test_vc_json_mode(
        input_audio_source="sean.mp3",  # Update this filename - This file needs to exist in 'vc_inputs/'
        target_voice_source="speaker_en/DAVID-2.mp3",
        export_formats=["wav", "mp3", "flac"],
        return_format="mp3",
        response_mode="stream"
    )
    
    # Test 3: JSON mode URL response - No file is uploaded
    print("\n" + "="*60)
    print("TEST 3: JSON Mode URL Response")
    client.test_vc_json_mode(
        input_audio_source="test_inputs/chatterbox-in-a-village-of-la-mancha.mp3",
        target_voice_source="speaker_en/jamie_vc_to_david-2.wav",
        export_formats=["wav", "mp3"],
        response_mode="url"
    )

    # Test 4: File upload streaming
    print("\n" + "="*60)
    print("TEST 4: File Upload Streaming")
    client.test_vc_file_upload(
        input_audio_file="jamie-01.mp3",  # Update this filename - This file needs to exist in 'tests/media'
        target_voice_source="speaker_en/jamie_vc_to_david-2.wav",
        export_formats="wav,mp3",
        response_mode="stream"
    )

    # Test 5: File upload with FLAC format
    print("\n" + "="*60)
    print("TEST 5: File Upload with FLAC Format")
    client.test_vc_file_upload(
        input_audio_file="jamie-02.mp3",  # Update this filename - This file needs to exist in 'tests/media'
        target_voice_source="test_voices/linda_johnson_02.mp3",
        export_formats="wav,mp3,flac",
        return_format="flac",
        response_mode="stream",
        chunk_sec=30,
        overlap_sec=0.2
    )

    # Test 6: File upload JSON response
    print("\n" + "="*60)
    print("TEST 6: File Upload JSON Response")
    client.test_vc_file_upload(
        input_audio_file="josh.mp3",  # Update this filename - This file needs to exist in 'tests/media'
        target_voice_source="test_voices/linda_johnson_02.mp3",
        export_formats="wav,mp3",
        response_mode="url"
    )
    
    print("\n🎉 VC Test Suite Complete!")
    print(f"📁 Check output files in: {client.media_dir}")
    print(f"\n📝 Note: Update input file names in the script with actual files you place in tests/media/")

if __name__ == "__main__":
    main()

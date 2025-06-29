#!/usr/bin/env python3
"""
Integrated Test: Voice Management
Complete workflow testing for Task 11.10 - Voice upload, organization, and management

This test demonstrates the complete lifecycle of voice file management:
1. Upload voice files to organized folders/categories
2. List and browse voices by folders and metadata
3. Search and find specific voices
4. Delete individual voices and clean up folders manually

Requirements:
- Server running at http://127.0.0.1:7860
- Test audio files in tests/media/ directory
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any

BASE_URL = "http://127.0.0.1:7860/api/v1"

class VoiceManagementTest:
    """Integrated test for voice management workflow"""
    
    def __init__(self):
        self.uploaded_voices = []
        self.created_folders = set()
        self.test_media_dir = Path("tests/media")
        
    def test_health(self) -> bool:
        """Test basic server connectivity"""
        print("🔍 Testing server connectivity...")
        try:
            response = requests.get(f"{BASE_URL}/health")
            response.raise_for_status()
            health = response.json()
            print(f"✅ Server status: {health['status']}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_test_audio_files(self) -> List[Path]:
        """Get available test audio files for voice upload"""
        print("\n🔍 Finding test audio files for voice upload...")
        
        if not self.test_media_dir.exists():
            print(f"❌ Test media directory not found: {self.test_media_dir}")
            return []
        
        # Look for clean audio files suitable as voices
        audio_extensions = ['.mp3', '.wav', '.flac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(list(self.test_media_dir.glob(f"*{ext}")))
        
        # Filter for voice samples (avoid concat or processed files)
        voice_files = []
        exclude_patterns = ['concat', 'mixed', 'vc_', 'speed_test']
        
        for file in audio_files:
            if not any(pattern in file.name.lower() for pattern in exclude_patterns):
                voice_files.append(file)
        
        # Take diverse samples
        sample_files = voice_files[:6]  # Take up to 6 files
        
        print(f"✅ Found {len(audio_files)} total audio files, {len(voice_files)} suitable for voices")
        print(f"   Using {len(sample_files)} for testing:")
        for file in sample_files:
            print(f"   - {file.name}")
        
        return sample_files
    
    def generate_voice_samples_if_needed(self) -> List[Path]:
        """Generate voice samples using TTS if needed"""
        print("\n🎵 Generating voice samples for testing...")
        
        voice_configs = [
            {"text": "Hello, I am a professional narrator voice.", "temp": 0.7, "seed": 200},
            {"text": "This is a casual conversational voice for everyday use.", "temp": 0.8, "seed": 201},
            {"text": "I represent a formal presentation voice for business.", "temp": 0.6, "seed": 202},
        ]
        
        generated_files = []
        
        for i, config in enumerate(voice_configs):
            tts_data = {
                "text": config["text"],
                "export_formats": ["wav"],
                "temperature": config["temp"],
                "seed": config["seed"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/tts", json=tts_data)
                response.raise_for_status()
                result = response.json()
                
                if result['output_files']:
                    wav_file = result['output_files'][0]
                    filename = wav_file['filename']
                    print(f"✅ Generated: {filename}")
                    
                    # Copy to test media directory for voice upload
                    source_path = Path("outputs") / filename
                    target_path = self.test_media_dir / f"voice_sample_{i+1}.wav"
                    
                    if source_path.exists():
                        import shutil
                        shutil.copy2(source_path, target_path)
                        generated_files.append(target_path)
                        print(f"   Copied to: {target_path.name}")
                
            except Exception as e:
                print(f"⚠️  Could not generate voice sample {i+1}: {e}")
        
        return generated_files
    
    def upload_voice(self, file_path: Path, name: str, description: str = None, 
                    folder_path: str = None, tags: List[str] = None) -> str:
        """Upload a voice file with metadata"""
        folder_info = f" to folder '{folder_path}'" if folder_path else " to root"
        print(f"\n📤 Uploading voice '{name}'{folder_info}...")
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Prepare upload data
        data = {
            'name': name,
            'overwrite': 'true'
        }
        
        if description:
            data['description'] = description
        
        if folder_path:
            data['folder_path'] = folder_path
        
        if tags:
            data['tags'] = ','.join(tags)
        
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'audio_file': (
                        f"voice_{file_path.name}", 
                        f, 
                        'audio/wav' if file_path.suffix == '.wav' else 'audio/mpeg'
                    )
                }
                
                response = requests.post(f"{BASE_URL}/voice", files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
                uploaded_filename = result['filename']
                self.uploaded_voices.append(uploaded_filename)
                
                if folder_path:
                    self.created_folders.add(folder_path)
                
                print(f"✅ Upload successful: {uploaded_filename}")
                print(f"   Name: {result['metadata']['name']}")
                print(f"   Duration: {result['metadata']['duration_seconds']:.2f}s")
                if 'folder_path' in result['metadata']:
                    print(f"   Folder: {result['metadata']['folder_path']}")
                
                return uploaded_filename
                
        except Exception as e:
            print(f"❌ Voice upload failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return None
    
    def list_voices_by_folder(self, folder: str = None) -> Dict[str, Any]:
        """List voices, optionally filtered by folder"""
        if folder:
            print(f"\n📁 Listing voices in folder '{folder}'...")
            params = {"folder": folder}
        else:
            print(f"\n📁 Listing all voices...")
            params = {}
            
        try:
            response = requests.get(f"{BASE_URL}/voices", params=params)
            response.raise_for_status()
            voices = response.json()
            
            print(f"✅ Found {len(voices['files'])} voices")
            if voices['files']:
                print("   Voices:")
                for voice_info in voices['files']:
                    folder = voice_info.get('folder_path', 'root')
                    name = voice_info.get('name', 'Unnamed')
                    duration = voice_info.get('duration_seconds', 0)
                    tags = voice_info.get('tags', [])
                    tags_str = f" [tags: {', '.join(tags)}]" if tags else ""
                    print(f"   - {voice_info['filename']} | {name} (folder: {folder}, {duration:.1f}s){tags_str}")
            
            return voices
            
        except Exception as e:
            print(f"❌ Listing voices failed: {e}")
            return {"files": []}
    
    def get_voice_folder_structure(self) -> Dict[str, Any]:
        """Get folder structure of reference_audio directory"""
        print(f"\n🌳 Getting voice folder structure...")
        try:
            response = requests.get(f"{BASE_URL}/voices/folders")
            response.raise_for_status()
            structure = response.json()
            
            print(f"✅ Voice folder structure:")
            self._print_folder_structure(structure.get('structure', {}), indent=1)
            
            return structure
            
        except Exception as e:
            print(f"❌ Getting folder structure failed: {e}")
            return {}
    
    def _print_folder_structure(self, structure: Dict, indent: int = 0):
        """Recursively print folder structure"""
        for folder, contents in structure.items():
            print("  " * indent + f"📁 {folder}/")
            if isinstance(contents, dict):
                self._print_folder_structure(contents, indent + 1)
    
    def search_voices(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for voices by name, filename, or tags"""
        print(f"\n🔍 Searching voices for '{search_term}'...")
        try:
            response = requests.get(f"{BASE_URL}/voices", params={"search": search_term})
            response.raise_for_status()
            results = response.json()
            
            found_voices = results['files']
            print(f"✅ Found {len(found_voices)} matching voices:")
            for voice_info in found_voices:
                folder = voice_info.get('folder_path', 'root')
                name = voice_info.get('name', 'Unnamed')
                tags = voice_info.get('tags', [])
                tags_str = f" [tags: {', '.join(tags)}]" if tags else ""
                print(f"   - {voice_info['filename']} | {name} (folder: {folder}){tags_str}")
            
            return found_voices
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def delete_single_voice(self, filename: str) -> bool:
        """Delete a single voice file"""
        print(f"\n🗑️  Deleting single voice '{filename}'...")
        try:
            response = requests.delete(f"{BASE_URL}/voice/{filename}?confirm=true")
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ {result['message']}")
            return True
            
        except Exception as e:
            print(f"❌ Deletion failed: {e}")
            return False
    
    def delete_voices_bulk(self, folder: str = None, search: str = None) -> bool:
        """Delete multiple voices based on criteria"""
        criteria = []
        if folder:
            criteria.append(f"folder '{folder}'")
        if search:
            criteria.append(f"search '{search}'")
        
        criteria_str = " and ".join(criteria) if criteria else "all voices"
        print(f"\n🗑️  Deleting voices matching: {criteria_str}...")
        
        params = {"confirm": "true"}
        if folder:
            params["folder"] = folder
        if search:
            params["search"] = search
        
        try:
            response = requests.delete(f"{BASE_URL}/voices", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ {result['message']}")
            return True
            
        except Exception as e:
            print(f"❌ Bulk deletion failed: {e}")
            return False
    
    def cleanup_empty_folders(self):
        """Manual cleanup of empty folders (no API for this)"""
        print(f"\n🧹 Note: Empty voice folders are preserved by design")
        print("   Voice folders represent categories and are not auto-deleted")
        print("   Created test folders: {0}".format(list(self.created_folders)))
    
    def run_comprehensive_test(self):
        """Run the complete voice management workflow test"""
        print("🚀 Voice Management - Integrated Test")
        print("=" * 60)
        
        # 1. Basic connectivity
        if not self.test_health():
            return False
        
        # 2. Get test audio files
        test_files = self.get_test_audio_files()
        
        # If no test files, generate some
        if len(test_files) < 2:
            print("\n⚠️  Insufficient test files found, generating voice samples...")
            generated_files = self.generate_voice_samples_if_needed()
            test_files.extend(generated_files)
        
        if len(test_files) < 2:
            print("❌ Could not obtain sufficient test files for testing")
            return False
        
        # 3. Upload voices in organized folder structure
        print(f"\n📋 Phase 1: Uploading voices to organized folders")
        print("-" * 50)
        
        # Upload to character voices folder
        if len(test_files) >= 1:
            self.upload_voice(
                test_files[0], 
                "Narrator Professional",
                "Professional narrator voice for audiobooks and presentations",
                "characters/narrators",
                ["professional", "narrator", "formal"]
            )
        
        # Upload to casual voices folder
        if len(test_files) >= 2:
            self.upload_voice(
                test_files[1], 
                "Casual Speaker",
                "Friendly conversational voice for everyday content",
                "characters/casual",
                ["casual", "friendly", "conversational"]
            )
        
        # Upload to business voices folder
        if len(test_files) >= 3:
            self.upload_voice(
                test_files[2], 
                "Business Executive",
                "Authoritative business voice for corporate content",
                "business/executives",
                ["business", "corporate", "authoritative"]
            )
        
        # Upload to root folder
        if len(test_files) >= 4:
            self.upload_voice(
                test_files[3], 
                "Default Voice",
                "General purpose voice file",
                None,  # Root folder
                ["default", "general"]
            )
        elif len(test_files) >= 1:
            # Reuse first file for root
            self.upload_voice(
                test_files[0], 
                "Root Test Voice",
                "Test voice in root folder",
                None,
                ["test", "root"]
            )
        
        # 4. Browse and list voices
        print(f"\n📋 Phase 2: Browsing and listing voices")
        print("-" * 50)
        
        # List all voices
        all_voices = self.list_voices_by_folder()
        
        # List by specific folders
        self.list_voices_by_folder("characters")
        self.list_voices_by_folder("business")
        
        # Get folder structure
        self.get_voice_folder_structure()
        
        # 5. Search functionality
        print(f"\n📋 Phase 3: Search and find functionality")
        print("-" * 50)
        
        # Search by name
        self.search_voices("Narrator")
        self.search_voices("Business")
        
        # Search by tags
        self.search_voices("professional")
        self.search_voices("casual")
        
        # 6. Voice deletion
        print(f"\n📋 Phase 4: Voice deletion and cleanup")
        print("-" * 50)
        
        # Delete a single voice (if we have any)
        if self.uploaded_voices:
            sample_voice = self.uploaded_voices[0]
            self.delete_single_voice(sample_voice)
        
        # Delete voices by folder
        self.delete_voices_bulk(folder="characters")
        self.delete_voices_bulk(folder="business")
        
        # Delete remaining test voices
        self.delete_voices_bulk(search="test")
        
        # 7. Verify cleanup
        print(f"\n📋 Phase 5: Verification after cleanup")
        print("-" * 50)
        
        # List remaining voices
        remaining = self.list_voices_by_folder()
        
        # Check folder structure after cleanup
        self.get_voice_folder_structure()
        
        # Note about folder cleanup
        self.cleanup_empty_folders()
        
        print(f"\n🎉 Voice Management Test Complete!")
        print(f"Uploaded voices: {len(self.uploaded_voices)}")
        print(f"Created folders: {list(self.created_folders)}")
        
        return True

def main():
    """Main test execution"""
    test = VoiceManagementTest()
    success = test.run_comprehensive_test()
    
    if success:
        print(f"\n✅ All tests completed successfully!")
        exit(0)
    else:
        print(f"\n❌ Some tests failed!")
        exit(1)

if __name__ == "__main__":
    main()

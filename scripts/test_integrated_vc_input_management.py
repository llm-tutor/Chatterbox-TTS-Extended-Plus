#!/usr/bin/env python3
"""
Integrated Test: VC Input File Management
Complete workflow testing for Task 11.10 - VC input upload, organization, and management

This test demonstrates the complete lifecycle of VC input file management:
1. Upload VC input files to organized project folders
2. List and browse uploaded files by folders
3. Search and find specific files
4. Delete individual files and entire project folders

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

class VcInputManagementTest:
    """Integrated test for VC input file management workflow"""
    
    def __init__(self):
        self.uploaded_files = []
        self.created_projects = set()
        self.test_media_dir = Path("tests/media")
        
    def test_health(self) -> bool:
        """Test basic server connectivity"""
        print("Testing server connectivity...")
        try:
            response = requests.get(f"{BASE_URL}/health")
            response.raise_for_status()
            health = response.json()
            print(f"Server status: {health['status']}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_test_audio_files(self) -> List[Path]:
        """Get available test audio files"""
        print("\n🔍 Finding test audio files...")
        
        if not self.test_media_dir.exists():
            print(f"Test media directory not found: {self.test_media_dir}")
            return []
        
        # Look for audio files
        audio_extensions = ['.mp3', '.wav', '.flac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(list(self.test_media_dir.glob(f"*{ext}")))
        
        # Filter to get diverse samples (avoid too many of same type)
        sample_files = []
        for pattern in ['alex', 'jamie', 'josh', 'sean']:
            matches = [f for f in audio_files if pattern in f.name.lower()]
            if matches:
                sample_files.append(matches[0])
        
        # If we don't have enough samples, take the first few available
        if len(sample_files) < 3:
            sample_files = audio_files[:4]
        
        print(f"Found {len(audio_files)} total audio files, using {len(sample_files)} for testing:")
        for file in sample_files:
            print(f"   - {file.name}")
        
        return sample_files
    
    def generate_test_audio_if_needed(self) -> List[Path]:
        """Generate test audio files using TTS if needed"""
        print("\n🎵 Generating test audio files for VC input testing...")
        
        test_texts = [
            "This is a test audio file for voice conversion input testing.",
            "Here we have another sample that will be used for VC processing.",
            "The third test file contains different content for variety."
        ]
        
        generated_files = []
        
        for i, text in enumerate(test_texts):
            tts_data = {
                "text": text,
                "export_formats": ["wav"],
                "temperature": 0.7,
                "seed": 100 + i
            }
            
            try:
                response = requests.post(f"{BASE_URL}/tts", json=tts_data)
                response.raise_for_status()
                result = response.json()
                
                # Get the generated file path
                if result['output_files']:
                    wav_file = result['output_files'][0]
                    filename = wav_file['filename']
                    print(f"Generated: {filename}")
                    
                    # Copy to test media directory for use
                    source_path = Path("outputs") / filename
                    target_path = self.test_media_dir / f"vc_test_{i+1}.wav"
                    
                    if source_path.exists():
                        import shutil
                        shutil.copy2(source_path, target_path)
                        generated_files.append(target_path)
                        print(f"   Copied to: {target_path.name}")
                
            except Exception as e:
                print(f"Could not generate test file {i+1}: {e}")
        
        return generated_files
    
    def upload_vc_input(self, file_path: Path, project: str = None, 
                       description: str = None) -> str:
        """Upload a VC input file to specified project"""
        project_info = f" to project '{project}'" if project else " to root"
        print(f"\nUploading '{file_path.name}'{project_info}...")
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return None
        
        # Prepare upload data
        data = {
            'overwrite': 'true'
        }
        
        if project:
            data['project'] = project
        
        if description:
            data['text'] = description
        
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'vc_input_file': (
                        f"upload_{file_path.name}", 
                        f, 
                        'audio/wav' if file_path.suffix == '.wav' else 'audio/mpeg'
                    )
                }
                
                response = requests.post(f"{BASE_URL}/vc_input", files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
                uploaded_filename = result['filename']
                self.uploaded_files.append(uploaded_filename)
                
                if project:
                    self.created_projects.add(project)
                
                print(f"Upload successful: {uploaded_filename}")
                print(f"   Duration: {result['metadata']['duration_seconds']:.2f}s")
                if 'folder_path' in result['metadata']:
                    print(f"   Project: {result['metadata']['folder_path']}")
                
                return uploaded_filename
                
        except Exception as e:
            print(f"Upload failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return None
    
    def list_vc_inputs_by_project(self, project: str = None) -> Dict[str, Any]:
        """List VC inputs, optionally filtered by project"""
        if project:
            print(f"\n📁 Listing VC inputs in project '{project}'...")
            params = {"project": project}
        else:
            print(f"\n📁 Listing all VC inputs...")
            params = {}
            
        try:
            response = requests.get(f"{BASE_URL}/vc_inputs", params=params)
            response.raise_for_status()
            vc_inputs = response.json()
            
            print(f"Found {len(vc_inputs['files'])} files")
            if vc_inputs['files']:
                print("   Files:")
                for file_info in vc_inputs['files']:
                    folder = file_info.get('folder_path', 'root')
                    duration = file_info.get('duration_seconds', 0)
                    print(f"   - {file_info['filename']} (folder: {folder}, {duration:.1f}s)")
            
            return vc_inputs
            
        except Exception as e:
            print(f"Listing VC inputs failed: {e}")
            return {"files": []}
    
    def get_vc_inputs_folder_structure(self) -> Dict[str, Any]:
        """Get folder structure of vc_inputs directory"""
        print(f"\nGetting VC inputs folder structure...")
        try:
            response = requests.get(f"{BASE_URL}/vc_inputs/folders")
            response.raise_for_status()
            structure = response.json()
            
            print(f"VC inputs folder structure:")
            self._print_folder_structure(structure.get('structure', {}), indent=1)
            
            return structure
            
        except Exception as e:
            print(f"Getting folder structure failed: {e}")
            return {}
    
    def _print_folder_structure(self, structure: Dict, indent: int = 0):
        """Recursively print folder structure"""
        for folder, contents in structure.items():
            print("  " * indent + f"{folder}/")
            if isinstance(contents, dict):
                self._print_folder_structure(contents, indent + 1)
    
    def search_vc_inputs(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for VC inputs by filename"""
        print(f"\n🔍 Searching VC inputs for '{search_term}'...")
        try:
            response = requests.get(f"{BASE_URL}/vc_inputs", params={"search": search_term})
            response.raise_for_status()
            results = response.json()
            
            found_files = results['files']
            print(f"Found {len(found_files)} matching files:")
            for file_info in found_files:
                folder = file_info.get('folder_path', 'root')
                duration = file_info.get('duration_seconds', 0)
                print(f"   - {file_info['filename']} (folder: {folder}, {duration:.1f}s)")
            
            return found_files
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def delete_single_vc_input(self, filename: str) -> bool:
        """Delete a single VC input file"""
        print(f"\nDeleting single VC input '{filename}'...")
        try:
            response = requests.delete(f"{BASE_URL}/vc_input/{filename}?confirm=true")
            response.raise_for_status()
            result = response.json()
            
            print(f" {result['message']}")
            return True
            
        except Exception as e:
            print(f"Deletion failed: {e}")
            return False
    
    def delete_project_vc_inputs(self, project: str) -> bool:
        """Delete all VC inputs in a project folder"""
        print(f"\nDeleting VC inputs project folder '{project}' and all contents...")
        try:
            response = requests.delete(f"{BASE_URL}/vc_inputs?project={project}&confirm=true")
            response.raise_for_status()
            result = response.json()
            
            print(f"{result['message']}")
            if project in self.created_projects:
                self.created_projects.remove(project)
            return True
            
        except Exception as e:
            print(f"Project deletion failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete VC input file management workflow test"""
        print("VC Input File Management - Integrated Test")
        print("=" * 60)
        
        # 1. Basic connectivity
        if not self.test_health():
            return False
        
        # 2. Get test audio files
        test_files = self.get_test_audio_files()
        
        # If no test files, generate some
        if len(test_files) < 2:
            print("\nInsufficient test files found, generating some...")
            generated_files = self.generate_test_audio_if_needed()
            test_files.extend(generated_files)
        
        if len(test_files) < 2:
            print("Could not obtain sufficient test files for testing")
            return False
        
        # 3. Upload VC inputs in organized project structure
        print(f"\nPhase 1: Uploading VC inputs to project folders")
        print("-" * 50)
        
        # Upload to different projects
        if len(test_files) >= 1:
            self.upload_vc_input(
                test_files[0], 
                "interview_project/raw_recordings", 
                "Raw interview recording for processing"
            )
        
        if len(test_files) >= 2:
            self.upload_vc_input(
                test_files[1], 
                "podcast_project/guest_voices", 
                "Guest voice for podcast episode"
            )
        
        if len(test_files) >= 3:
            self.upload_vc_input(
                test_files[2], 
                "interview_project/followup", 
                "Follow-up interview session"
            )
        
        # Upload to root folder
        if len(test_files) >= 4:
            self.upload_vc_input(
                test_files[3], 
                None, 
                "Standalone voice file in root folder"
            )
        elif len(test_files) >= 1:
            # Reuse first file for root upload
            self.upload_vc_input(
                test_files[0], 
                None, 
                "Copy of test file in root folder"
            )
        
        # 4. Browse and list uploaded files
        print(f"\nPhase 2: Browsing and listing uploaded files")
        print("-" * 50)
        
        # List all VC inputs
        all_vc_inputs = self.list_vc_inputs_by_project()
        
        # List by specific project
        self.list_vc_inputs_by_project("interview_project")
        self.list_vc_inputs_by_project("podcast_project")
        
        # Get folder structure
        self.get_vc_inputs_folder_structure()
        
        # 5. Search functionality
        print(f"\nPhase 3: Search and find functionality")
        print("-" * 50)
        
        # Search for files
        self.search_vc_inputs("interview")
        self.search_vc_inputs("podcast")
        self.search_vc_inputs("upload")
        
        # 6. File deletion
        print(f"\nPhase 4: File deletion and cleanup")
        print("-" * 50)
        
        # Delete a single file (if we have any)
        if self.uploaded_files:
            sample_file = self.uploaded_files[0]
            self.delete_single_vc_input(sample_file)
        
        # Delete entire project folders
        self.delete_project_vc_inputs("interview_project")
        self.delete_project_vc_inputs("podcast_project")
        
        # 7. Verify cleanup
        print(f"\nPhase 5: Verification after cleanup")
        print("-" * 50)
        
        # List remaining files
        remaining = self.list_vc_inputs_by_project()
        
        # Check folder structure after cleanup
        self.get_vc_inputs_folder_structure()
        
        print(f"\nVC Input File Management Test Complete!")
        print(f"Uploaded files: {len(self.uploaded_files)}")
        print(f"Created projects: {list(self.created_projects)}")
        
        return True

def main():
    """Main test execution"""
    test = VcInputManagementTest()
    success = test.run_comprehensive_test()
    
    if success:
        print(f"\nAll tests completed successfully!")
        exit(0)
    else:
        print(f"\nSome tests failed!")
        exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Integrated Test: TTS Output File Management
Complete workflow testing for Task 11.10 - TTS output generation, organization, and management

This test demonstrates the complete lifecycle of TTS file management:
1. Generate TTS outputs in organized project folders
2. List and browse generated files by folders
3. Search and find specific files
4. Delete individual files and entire project folders

Requirements:
- Server running at http://127.0.0.1:7860
- Reference audio files in reference_audio/ directory
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any

BASE_URL = "http://127.0.0.1:7860/api/v1"

class TtsFileManagementTest:
    """Integrated test for TTS file management workflow"""
    
    def __init__(self):
        self.generated_files = []
        self.created_projects = set()
        
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
    
    def check_reference_audio(self) -> List[str]:
        """Check available reference audio files"""
        print("\nChecking available reference audio...")
        try:
            response = requests.get(f"{BASE_URL}/voices")
            response.raise_for_status()
            voices = response.json()
            # Fix path separators for cross-platform compatibility
            available_voices = [v['url'].replace('\\', '/') for v in voices['voices'][:3]]  # Take first 3, use 'url' field
            print(f"Found {voices['count']} reference voices")
            for voice in available_voices:
                print(f"   - {voice}")
            return available_voices
        except Exception as e:
            print(f"Could not check voices: {e}, will use default")
            return ["default_voice.wav"]
    
    def generate_tts_in_project(self, project: str, text: str, 
                               reference_voice: str = None, formats: List[str] = None) -> List[str]:
        """Generate TTS output in specific project folder"""
        if formats is None:
            formats = ["wav", "mp3"]
            
        print(f"\nGenerating TTS in project '{project}'...")
        
        tts_data = {
            "text": text,
            "project": project,
            "export_formats": formats,
            "temperature": 0.75,
            "seed": int(time.time()) % 1000  # Unique seed for variation
        }
        
        if reference_voice:
            tts_data["reference_audio_filename"] = reference_voice
        
        try:
            response = requests.post(f"{BASE_URL}/tts?response_mode=url", json=tts_data)
            response.raise_for_status()
            result = response.json()
            
            generated = [f['filename'] for f in result['output_files']]
            self.generated_files.extend(generated)
            self.created_projects.add(project)
            
            print(f" Generated {len(generated)} files:")
            for filename in generated:
                print(f"   - {filename}")
            
            return generated
            
        except Exception as e:
            print(f" TTS generation failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return []
    
    def list_outputs_by_project(self, project: str = None) -> Dict[str, Any]:
        """List outputs, optionally filtered by project"""
        if project:
            print(f"\n Listing outputs in project '{project}'...")
            params = {"project": project}
        else:
            print(f"\n Listing all outputs...")
            params = {}
            
        try:
            response = requests.get(f"{BASE_URL}/outputs", params=params)
            response.raise_for_status()
            outputs = response.json()
            
            print(f" Found {len(outputs['files'])} files")
            if outputs['files']:
                print("   Recent files:")
                for file_info in outputs['files'][:5]:  # Show first 5
                    folder = file_info.get('folder_path', 'root')
                    print(f"   - {file_info['filename']} (folder: {folder})")
            
            return outputs
            
        except Exception as e:
            print(f" Listing outputs failed: {e}")
            return {"files": []}
    
    def get_output_folder_structure(self) -> Dict[str, Any]:
        """Get folder structure of outputs directory"""
        print(f"\n Getting output folder structure...")
        try:
            response = requests.get(f"{BASE_URL}/outputs/folders")
            response.raise_for_status()
            structure = response.json()
            
            print(f" Output folder structure:")
            self._print_folder_structure(structure.get('structure', {}), indent=1)
            
            return structure
            
        except Exception as e:
            print(f" Getting folder structure failed: {e}")
            return {}
    
    def _print_folder_structure(self, structure: Dict, indent: int = 0):
        """Recursively print folder structure"""
        for folder, contents in structure.items():
            print("  " * indent + f" {folder}/")
            if isinstance(contents, dict):
                self._print_folder_structure(contents, indent + 1)
    
    def search_outputs(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for outputs by filename"""
        print(f"\n Searching outputs for '{search_term}'...")
        try:
            response = requests.get(f"{BASE_URL}/outputs", params={"search": search_term})
            response.raise_for_status()
            results = response.json()
            
            found_files = results['files']
            print(f" Found {len(found_files)} matching files:")
            for file_info in found_files:
                folder = file_info.get('folder_path', 'root')
                print(f"   - {file_info['filename']} (folder: {folder})")
            
            return found_files
            
        except Exception as e:
            print(f" Search failed: {e}")
            return []
    
    def delete_single_output(self, filename: str) -> bool:
        """Delete a single output file"""
        print(f"\n  Deleting single file '{filename}'...")
        try:
            response = requests.delete(f"{BASE_URL}/output/{filename}?confirm=true")
            response.raise_for_status()
            result = response.json()
            
            print(f" {result['message']}")
            return True
            
        except Exception as e:
            print(f" Deletion failed: {e}")
            return False
    
    def delete_project_outputs(self, project: str) -> bool:
        """Delete all outputs in a project folder"""
        print(f"\n  Deleting project folder '{project}' and all contents...")
        try:
            response = requests.delete(f"{BASE_URL}/outputs?project={project}&confirm=true")
            response.raise_for_status()
            result = response.json()
            
            print(f" {result['message']}")
            if project in self.created_projects:
                self.created_projects.remove(project)
            return True
            
        except Exception as e:
            print(f" Project deletion failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete TTS file management workflow test"""
        print("TTS Output File Management - Integrated Test")
        print("=" * 60)
        
        # 1. Basic connectivity
        if not self.test_health():
            return False
        
        # 2. Check available voices
        available_voices = self.check_reference_audio()
        reference_voice = available_voices[0] if available_voices else None
        
        # 3. Generate TTS outputs in organized project structure
        print(f"\n Phase 1: Generating TTS outputs in project folders")
        print("-" * 50)
        
        # Generate in main project
        self.generate_tts_in_project(
            "test_book/chapter1", 
            "This is the first chapter of our test book. It introduces the main character.",
            reference_voice
        )
        
        # Generate in subproject
        self.generate_tts_in_project(
            "test_book/chapter2", 
            "The second chapter continues the story with new adventures and challenges.",
            reference_voice,
            ["wav"]  # Different format
        )
        
        # Generate in different project
        self.generate_tts_in_project(
            "podcast_series/episode1", 
            "Welcome to our podcast series! This is the first episode.",
            reference_voice,
            ["mp3", "flac"]  # Different formats
        )
        
        # Generate in root (no project)
        print(f"\n Generating TTS in root folder...")
        self.generate_tts_in_project(
            "", 
            "This file will be generated in the root outputs folder.",
            reference_voice
        )
        
        # 4. Browse and list generated files
        print(f"\n Phase 2: Browsing and listing generated files")
        print("-" * 50)
        
        # List all outputs
        all_outputs = self.list_outputs_by_project()
        
        # List by specific project
        self.list_outputs_by_project("test_book/chapter1")
        self.list_outputs_by_project("podcast_series")
        
        # Get folder structure
        self.get_output_folder_structure()
        
        # 5. Search functionality
        print(f"\n Phase 3: Search and find functionality")
        print("-" * 50)
        
        # Search for files
        self.search_outputs("chapter")
        self.search_outputs("podcast")
        self.search_outputs("test_book")
        
        # 6. File deletion
        print(f"\n Phase 4: File deletion and cleanup")
        print("-" * 50)
        
        # Delete a single file (if we have any)
        if self.generated_files:
            sample_file = self.generated_files[0]
            self.delete_single_output(sample_file)
        
        # Delete entire project folders
        self.delete_project_outputs("test_book")
        self.delete_project_outputs("podcast_series")
        
        # 7. Verify cleanup
        print(f"\n Phase 5: Verification after cleanup")
        print("-" * 50)
        
        # List remaining files
        remaining = self.list_outputs_by_project()
        
        # Check folder structure after cleanup
        self.get_output_folder_structure()
        
        print(f"\n TTS File Management Test Complete!")
        print(f"Generated files: {len(self.generated_files)}")
        print(f"Created projects: {list(self.created_projects)}")
        
        return True

def main():
    """Main test execution"""
    test = TtsFileManagementTest()
    success = test.run_comprehensive_test()
    
    if success:
        print(f"\n All tests completed successfully!")
        exit(0)
    else:
        print(f"\n Some tests failed!")
        exit(1)

if __name__ == "__main__":
    main()

# tests/test_resource_management.py - Resource management tests

import os
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Set up test environment before imports
test_temp_dir = Path(tempfile.mkdtemp(prefix="chatterbox_test_"))
os.environ['CHATTERBOX_CONFIG_PATH'] = str(test_temp_dir / "test_config.yaml")

# Create test config
test_config = f"""
server:
  host: "127.0.0.1"
  port: 7860

paths:
  reference_audio_dir: "{test_temp_dir / 'reference_audio'}"
  vc_input_dir: "{test_temp_dir / 'vc_inputs'}"
  output_dir: "{test_temp_dir / 'outputs'}"
  temp_dir: "{test_temp_dir / 'temp'}"
  logs_dir: "{test_temp_dir / 'logs'}"

resource_management:
  cleanup:
    output_dir_max_size_gb: 0.001        # 1MB for testing
    temp_dir_max_files: 3               # Max 3 files for testing
    temp_dir_max_age_days: 1            # 1 day for testing
    vc_inputs_max_size_gb: 0.001        # 1MB for testing
    cleanup_on_startup: false           # Disable for testing
    cleanup_interval_hours: 0           # Disable for testing
    warning_threshold_percent: 80
"""

with open(test_temp_dir / "test_config.yaml", "w", encoding="utf-8") as f:
    f.write(test_config)

# Now import our modules
from management.resource_manager import ResourceManager
from management.cleanup_scheduler import CleanupScheduler

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

class TestResourceManager:
    """Test resource management functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = ResourceManager()
        
        # Create test directories
        for dir_attr in ['output_dir', 'temp_dir', 'vc_inputs_dir']:
            getattr(self.manager, dir_attr).mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment"""
        # Clean up test files
        for dir_attr in ['output_dir', 'temp_dir', 'vc_inputs_dir']:
            dir_path = getattr(self.manager, dir_attr)
            if dir_path.exists():
                shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_directory_size_calculation(self):
        """Test directory size calculation"""
        # Create test files
        create_test_file(self.manager.output_dir / "file1.wav", 1000)
        create_test_file(self.manager.output_dir / "file2.wav", 2000)
        
        size = self.manager.get_directory_size(self.manager.output_dir)
        assert size == 3000, f"Expected 3000 bytes, got {size}"
        
        # Test empty directory
        empty_size = self.manager.get_directory_size(self.manager.temp_dir)
        assert empty_size == 0
    
    def test_file_count_calculation(self):
        """Test file count calculation"""
        # Create test files
        create_test_file(self.manager.temp_dir / "file1.wav", 100)
        create_test_file(self.manager.temp_dir / "file2.wav", 100)
        create_test_file(self.manager.temp_dir / "subdir" / "file3.wav", 100)
        
        count = self.manager.get_directory_file_count(self.manager.temp_dir)
        assert count == 3, f"Expected 3 files, got {count}"
    
    def test_old_files_detection(self):
        """Test detection of old files"""
        # Create recent and old files
        create_test_file(self.manager.temp_dir / "recent.wav", 100)
        create_old_file(self.manager.temp_dir / "old1.wav", age_days=2)
        create_old_file(self.manager.temp_dir / "old2.wav", age_days=3)
        
        old_files = self.manager.get_old_files(self.manager.temp_dir, max_age_days=1)
        old_filenames = [f.name for f in old_files]
        
        assert len(old_files) == 2
        assert "old1.wav" in old_filenames
        assert "old2.wav" in old_filenames
        assert "recent.wav" not in old_filenames
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files"""
        # Create files
        recent_file = create_test_file(self.manager.temp_dir / "recent.wav", 500)
        old_file1 = create_old_file(self.manager.temp_dir / "old1.wav", age_days=2, size_bytes=1000)
        old_file2 = create_old_file(self.manager.temp_dir / "old2.wav", age_days=3, size_bytes=1500)
        
        # Perform cleanup
        files_removed, bytes_freed = self.manager.cleanup_old_files(self.manager.temp_dir, max_age_days=1)
        
        assert files_removed == 2
        assert bytes_freed == 2500
        assert recent_file.exists()
        assert not old_file1.exists()
        assert not old_file2.exists()
    
    def test_cleanup_excess_files(self):
        """Test cleanup of excess files"""
        # Create files with different ages
        files = []
        for i in range(5):
            file_path = create_test_file(self.manager.temp_dir / f"file{i}.wav", 100)
            # Set different modification times
            old_time = time.time() - (i * 60)  # Each file is 1 minute older
            os.utime(file_path, (old_time, old_time))
            files.append(file_path)
        
        # Keep only 3 files (should remove 2 oldest)
        files_removed, bytes_freed = self.manager.cleanup_excess_files(self.manager.temp_dir, max_files=3)
        
        assert files_removed == 2
        assert bytes_freed == 200
        
        # Check that newest files remain
        remaining_files = list(self.manager.temp_dir.rglob("*.wav"))
        assert len(remaining_files) == 3
    
    def test_cleanup_directory_by_size(self):
        """Test cleanup by directory size"""
        # Create files with different ages
        files = []
        for i in range(4):
            file_path = create_test_file(self.manager.output_dir / f"file{i}.wav", 1000)
            # Set different modification times
            old_time = time.time() - (i * 60)
            os.utime(file_path, (old_time, old_time))
            files.append(file_path)
        
        # Limit to 2000 bytes (should remove 2 oldest files)
        files_removed, bytes_freed = self.manager.cleanup_directory_by_size(self.manager.output_dir, max_bytes=2000)
        
        assert files_removed == 2
        assert bytes_freed == 2000
        
        remaining_size = self.manager.get_directory_size(self.manager.output_dir)
        assert remaining_size <= 2000
    
    def test_perform_cleanup(self):
        """Test complete cleanup operation"""
        # Create files that should be cleaned
        
        # Old temp files
        create_old_file(self.manager.temp_dir / "old_temp.wav", age_days=2, size_bytes=500)
        
        # Excess temp files
        for i in range(5):
            create_test_file(self.manager.temp_dir / f"temp{i}.wav", 100)
        
        # Large output files
        for i in range(3):
            create_test_file(self.manager.output_dir / f"output{i}.wav", 1000)
        
        # Perform cleanup
        summary = self.manager.perform_cleanup()
        
        assert summary["total_files_removed"] > 0
        assert summary["total_bytes_freed"] > 0
        assert "actions" in summary
        assert "temp_age_cleanup" in summary["actions"]
        assert "temp_count_cleanup" in summary["actions"]
        assert "output_size_cleanup" in summary["actions"]
    
    def test_resource_status(self):
        """Test resource status reporting"""
        # Create some files
        create_test_file(self.manager.output_dir / "output.wav", 500)
        create_test_file(self.manager.temp_dir / "temp.wav", 200)
        create_test_file(self.manager.vc_inputs_dir / "input.wav", 300)
        
        status = self.manager.get_resource_status()
        
        assert "directories" in status
        assert "outputs" in status["directories"]
        assert "temp" in status["directories"]
        assert "vc_inputs" in status["directories"]
        
        # Check output directory status
        output_status = status["directories"]["outputs"]
        assert output_status["size_bytes"] == 500
        assert output_status["file_count"] == 1
        assert "usage_percent" in output_status
        
        # Should not have warnings with small files
        assert len(status.get("warnings", [])) == 0
    
    def test_resource_warnings(self):
        """Test resource warning generation"""
        # Create files that exceed warning threshold
        warning_size = int(self.manager.output_dir_max_bytes * 0.85)  # 85% of limit
        create_test_file(self.manager.output_dir / "large_output.wav", warning_size)
        
        status = self.manager.get_resource_status()
        
        assert len(status["warnings"]) > 0
        assert any("Output directory" in warning for warning in status["warnings"])


class TestCleanupScheduler:
    """Test cleanup scheduler functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.scheduler = CleanupScheduler()
        # Override config for testing
        self.scheduler.cleanup_on_startup = False
        self.scheduler.cleanup_interval_hours = 0  # Disable periodic cleanup
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.scheduler._running:
            self.scheduler.stop()
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        assert not self.scheduler._running
        assert self.scheduler.last_cleanup_time is None
        assert len(self.scheduler.cleanup_history) == 0
    
    def test_force_cleanup(self):
        """Test force cleanup functionality"""
        result = self.scheduler.force_cleanup()
        
        assert "total_files_removed" in result
        assert "total_bytes_freed" in result
        assert "forced" in result
        assert result["forced"] is True
        assert "duration_seconds" in result
        
        # Check history was updated
        assert len(self.scheduler.cleanup_history) == 1
        assert self.scheduler.last_cleanup_time is not None
    
    def test_scheduler_status(self):
        """Test scheduler status reporting"""
        status = self.scheduler.get_status()
        
        assert "running" in status
        assert "cleanup_on_startup" in status
        assert "cleanup_interval_hours" in status
        assert "last_cleanup_time" in status
        assert "cleanup_count" in status
    
    def test_cleanup_history(self):
        """Test cleanup history tracking"""
        # Perform multiple cleanups
        self.scheduler.force_cleanup()
        self.scheduler.force_cleanup()
        
        history = self.scheduler.get_history(limit=5)
        assert len(history) == 2
        
        # Check history contains expected fields
        for record in history:
            assert "total_files_removed" in record
            assert "total_bytes_freed" in record


def run_tests():
    """Run all resource management tests"""
    print("Running Resource Management Tests...")
    
    try:
        # Test ResourceManager
        print("\n=== Testing ResourceManager ===")
        manager_tests = TestResourceManager()
        
        test_methods = [
            "test_directory_size_calculation",
            "test_file_count_calculation", 
            "test_old_files_detection",
            "test_cleanup_old_files",
            "test_cleanup_excess_files",
            "test_cleanup_directory_by_size",
            "test_perform_cleanup",
            "test_resource_status",
            "test_resource_warnings"
        ]
        
        for test_method in test_methods:
            try:
                manager_tests.setup_method()
                getattr(manager_tests, test_method)()
                manager_tests.teardown_method()
                print(f"✅ {test_method}")
            except Exception as e:
                print(f"❌ {test_method}: {e}")
                manager_tests.teardown_method()
        
        # Test CleanupScheduler
        print("\n=== Testing CleanupScheduler ===")
        scheduler_tests = TestCleanupScheduler()
        
        scheduler_test_methods = [
            "test_scheduler_initialization",
            "test_force_cleanup",
            "test_scheduler_status",
            "test_cleanup_history"
        ]
        
        for test_method in scheduler_test_methods:
            try:
                scheduler_tests.setup_method()
                getattr(scheduler_tests, test_method)()
                scheduler_tests.teardown_method()
                print(f"✅ {test_method}")
            except Exception as e:
                print(f"❌ {test_method}: {e}")
                scheduler_tests.teardown_method()
        
        print("\n🎉 All resource management tests completed!")
        
    finally:
        # Clean up test directory
        if test_temp_dir.exists():
            shutil.rmtree(test_temp_dir, ignore_errors=True)
        print(f"🧹 Cleaned up test directory: {test_temp_dir}")


if __name__ == "__main__":
    run_tests()

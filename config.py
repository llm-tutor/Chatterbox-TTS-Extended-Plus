# config.py - Configuration management for Chatterbox TTS Extended Plus
# Adapted from Chatterbox-TTS-Server with modifications for Extended Plus project

import os
import logging
import yaml
import shutil
from copy import deepcopy
from threading import Lock
from typing import Dict, Any, Optional, List
import torch
from pathlib import Path

# Standard logger setup
logger = logging.getLogger(__name__)

# --- File Path Constants ---
CONFIG_FILE_PATH = Path("config.yaml")

# --- Default Directory Paths ---
DEFAULT_LOGS_PATH = Path("logs")
DEFAULT_REFERENCE_AUDIO_PATH = Path("reference_audio")  # For TTS reference and VC targets
DEFAULT_VC_INPUT_PATH = Path("vc_inputs")  # For VC input files
DEFAULT_OUTPUT_PATH = Path("outputs")  # For generated audio outputs
DEFAULT_TEMP_PATH = Path("temp")  # For temporary files (downloads, etc.)

# --- Default Configuration Structure ---
DEFAULT_CONFIG: Dict[str, Any] = {
    "server": {
        "host": "127.0.0.1",  # Local only by default for personal use
        "port": 7860,  # Gradio's default port
        "log_level": "INFO",
        "log_file_path": str(DEFAULT_LOGS_PATH / "chatterbox_extended.log"),
        "log_file_max_size_mb": 10,
        "log_file_backup_count": 5,
    },
    "paths": {
        "reference_audio_dir": str(DEFAULT_REFERENCE_AUDIO_PATH),
        "vc_input_dir": str(DEFAULT_VC_INPUT_PATH),
        "output_dir": str(DEFAULT_OUTPUT_PATH),
        "temp_dir": str(DEFAULT_TEMP_PATH),
        "logs_dir": str(DEFAULT_LOGS_PATH),
    },
    "models": {
        "device": "auto",  # auto, cuda, cpu
        "preload_models": True,
    },
    "api": {
        "max_text_length": 10000,
        "cleanup_temp_files": True,
        "enable_url_downloads": True,
        "download_timeout_seconds": 30,
    },
    "tts_defaults": {
        "exaggeration": 0.5,
        "temperature": 0.75,
        "cfg_weight": 1.0,
        "seed": 0,
        "num_candidates_per_chunk": 3,
        "max_attempts_per_candidate": 3,
        "bypass_whisper_checking": False,
        "whisper_model_name": "medium",
        "use_faster_whisper": True,
        "use_longest_transcript_on_fail": True,
        "enable_batching": False,
        "smart_batch_short_sentences": True,
        "to_lowercase": True,
        "normalize_spacing": True,
        "fix_dot_letters": True,
        "remove_reference_numbers": True,
        "use_auto_editor": False,
        "ae_threshold": 0.06,
        "ae_margin": 0.2,
        "normalize_audio": False,
        "normalize_method": "ebu",
        "normalize_level": -24.0,
        "normalize_tp": -2.0,
        "normalize_lra": 7.0,
        "disable_watermark": True,
        "export_formats": ["wav", "mp3"],
    },
    "vc_defaults": {
        "chunk_sec": 60,
        "overlap_sec": 0.1,
        "disable_watermark": True,
        "export_formats": ["wav", "mp3"],
    },
    "ui": {
        "title": "Chatterbox TTS Extended Plus",
        "mount_path": "/ui",
        "enable_ui": True,
    },
}


def _ensure_default_paths_exist():
    """Create default directories if they don't exist"""
    paths_to_check = [
        Path(DEFAULT_CONFIG["server"]["log_file_path"]).parent,
        Path(DEFAULT_CONFIG["paths"]["reference_audio_dir"]),
        Path(DEFAULT_CONFIG["paths"]["vc_input_dir"]),
        Path(DEFAULT_CONFIG["paths"]["output_dir"]),
        Path(DEFAULT_CONFIG["paths"]["temp_dir"]),
        Path(DEFAULT_CONFIG["paths"]["logs_dir"]),
    ]
    for path in paths_to_check:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating default directory {path}: {e}")


def _deep_merge_dicts(source: Dict, destination: Dict) -> Dict:
    """Recursively merge source dict into destination dict"""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            if isinstance(node, dict):
                _deep_merge_dicts(value, node)
            else:
                destination[key] = deepcopy(value)
        else:
            destination[key] = value
    return destination


def _set_nested_value(d: Dict, keys: List[str], value: Any):
    """Set value in nested dictionary using list of keys"""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def _get_nested_value(d: Dict, keys: List[str], default: Any = None) -> Any:
    """Get value from nested dictionary using list of keys"""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d


class YamlConfigManager:
    """Configuration manager for YAML-based settings"""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._lock = Lock()
        self.load_config()

    def _load_defaults(self) -> Dict[str, Any]:
        """Return deep copy of default configuration"""
        _ensure_default_paths_exist()
        return deepcopy(DEFAULT_CONFIG)

    def _resolve_paths_and_device(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve device settings and convert string paths to Path objects"""
        # Resolve device setting
        current_device = _get_nested_value(config_data, ["models", "device"], "auto")
        if current_device == "auto":
            resolved_device = self._detect_best_device()
            _set_nested_value(config_data, ["models", "device"], resolved_device)
        elif current_device not in ["cuda", "cpu"]:
            logger.warning(f"Invalid device '{current_device}', using auto-detection")
            resolved_device = self._detect_best_device()
            _set_nested_value(config_data, ["models", "device"], resolved_device)

        final_device = _get_nested_value(config_data, ["models", "device"])
        logger.info(f"Device resolved to: {final_device}")

        # Convert paths to Path objects
        path_sections = {
            "server": ["log_file_path"],
            "paths": ["reference_audio_dir", "vc_input_dir", "output_dir", "temp_dir", "logs_dir"],
        }
        
        for section, keys in path_sections.items():
            if section in config_data:
                for key in keys:
                    current_path = _get_nested_value(config_data, [section, key])
                    if isinstance(current_path, str):
                        _set_nested_value(config_data, [section, key], Path(current_path))
        
        return config_data

    def _detect_best_device(self) -> str:
        """Detect the best available device for processing"""
        if not torch.cuda.is_available():
            logger.info("CUDA not available, using CPU")
            return "cpu"

        try:
            # Test CUDA functionality
            test_tensor = torch.tensor([1.0]).cuda()
            test_tensor = test_tensor.cpu()
            logger.info("CUDA test successful, using CUDA")
            return "cuda"
        except Exception as e:
            logger.warning(f"CUDA test failed: {e}, using CPU")
            return "cpu"

    def _prepare_config_for_saving(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Path objects to strings for YAML serialization"""
        config_copy = deepcopy(config_dict)
        
        path_sections = {
            "server": ["log_file_path"],
            "paths": ["reference_audio_dir", "vc_input_dir", "output_dir", "temp_dir", "logs_dir"],
        }
        
        for section, keys in path_sections.items():
            if section in config_copy:
                for key in keys:
                    current_path = _get_nested_value(config_copy, [section, key])
                    if isinstance(current_path, Path):
                        _set_nested_value(config_copy, [section, key], str(current_path))
        
        return config_copy

    def load_config(self):
        """Load configuration from YAML file"""
        with self._lock:
            base_defaults = self._load_defaults()

            if CONFIG_FILE_PATH.exists():
                logger.info(f"Loading configuration from: {CONFIG_FILE_PATH}")
                try:
                    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                        yaml_data = yaml.safe_load(f)
                    
                    if isinstance(yaml_data, dict):
                        effective_config = deepcopy(base_defaults)
                        _deep_merge_dicts(yaml_data, effective_config)
                        self.config = effective_config
                        logger.info("Configuration loaded and merged successfully")
                    else:
                        logger.error("Invalid YAML format, using defaults")
                        self.config = base_defaults
                        self._save_config_yaml_internal(self.config)
                        
                except yaml.YAMLError as e:
                    logger.error(f"YAML parsing error: {e}, using defaults")
                    self.config = base_defaults
                    self._save_config_yaml_internal(self.config)
                except Exception as e:
                    logger.error(f"Error loading config: {e}, using defaults")
                    self.config = base_defaults
            else:
                logger.info("Config file not found, creating default configuration")
                self.config = base_defaults
                self._save_config_yaml_internal(self.config)

            # Resolve paths and device
            self.config = self._resolve_paths_and_device(self.config)
            return self.config

    def _save_config_yaml_internal(self, config_dict: Dict[str, Any]) -> bool:
        """Internal method to save config to YAML file"""
        prepared_config = self._prepare_config_for_saving(config_dict)
        temp_file = CONFIG_FILE_PATH.with_suffix(".tmp")
        backup_file = CONFIG_FILE_PATH.with_suffix(".bak")

        try:
            # Write to temp file first
            with open(temp_file, "w", encoding="utf-8") as f:
                yaml.dump(prepared_config, f, default_flow_style=False, 
                         sort_keys=False, indent=2)

            # Backup existing file
            if CONFIG_FILE_PATH.exists():
                shutil.move(str(CONFIG_FILE_PATH), str(backup_file))

            # Move temp to main file
            shutil.move(str(temp_file), str(CONFIG_FILE_PATH))
            logger.info(f"Configuration saved to {CONFIG_FILE_PATH}")
            
            # Clean up backup
            if backup_file.exists():
                backup_file.unlink()
            
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            # Restore from backup if needed
            if backup_file.exists() and not CONFIG_FILE_PATH.exists():
                shutil.move(str(backup_file), str(CONFIG_FILE_PATH))
            return False

    def save_config_yaml(self) -> bool:
        """Save current configuration to YAML file"""
        with self._lock:
            return self._save_config_yaml_internal(self.config)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot-separated key path"""
        keys = key_path.split(".")
        with self._lock:
            value = _get_nested_value(self.config, keys, default)
        return deepcopy(value) if isinstance(value, (dict, list)) else value

    def get_all(self) -> Dict[str, Any]:
        """Get complete configuration as deep copy"""
        with self._lock:
            return deepcopy(self.config)

    def update_and_save(self, partial_update: Dict[str, Any]) -> bool:
        """Update configuration with partial data and save"""
        if not isinstance(partial_update, dict):
            logger.error("Invalid update data: must be dictionary")
            return False

        with self._lock:
            try:
                config_copy = deepcopy(self.config)
                _deep_merge_dicts(partial_update, config_copy)
                resolved_config = self._resolve_paths_and_device(config_copy)

                if self._save_config_yaml_internal(resolved_config):
                    self.config = resolved_config
                    logger.info("Configuration updated and saved successfully")
                    return True
                else:
                    logger.error("Failed to save updated configuration")
                    return False
            except Exception as e:
                logger.error(f"Error updating configuration: {e}")
                return False


# Singleton instance
config_manager = YamlConfigManager()

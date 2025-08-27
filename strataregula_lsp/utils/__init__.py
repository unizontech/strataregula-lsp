"""
Utilities package for StrataRegula LSP
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """Configuration loader for StrataRegula LSP settings"""
    
    def __init__(self):
        self._config = {}
        self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration"""
        self._config = {
            "validation": {
                "on_save": True,
                "on_change": False
            },
            "completion": {
                "max_items": 50,
                "show_documentation": True
            },
            "pattern_learning": {
                "enabled": True,
                "cache_size": 1000
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation key"""
        keys = key.split('.')
        target = self._config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def load_from_file(self, file_path: str) -> bool:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
                return True
        except Exception:
            pass
        return False
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with defaults"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self._config, user_config)


__all__ = ["ConfigLoader"]
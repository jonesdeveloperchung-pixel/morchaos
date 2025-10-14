"""Configuration management for pyutils."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union

def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON configuration with environment variable overrides."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    with config_path.open('r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Override with environment variables
    for key, value in os.environ.items():
        if key.startswith('PYUTILS_'):
            config_key = key[8:].lower()  # Remove PYUTILS_ prefix
            config[config_key] = value
    
    return config

def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get a configuration value with dot notation support."""
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value
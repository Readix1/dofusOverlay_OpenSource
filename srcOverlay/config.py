import json
import threading
from typing import Any, Dict
import os

class Config:
    _config_data: Dict[str, Any] = None
    _lock = threading.Lock()
    _config_path = None

    @classmethod
    def _get_config_path(cls):
        # Chemin relatif depuis ce fichier
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rel_path = os.path.join('ressources', 'config.json')
        if not os.path.exists(rel_path):
            # Essayer _internal/ressources/config.json
            rel_path = os.path.join(base_dir, 'ressources', 'config.json')
        
        print(f"Using config path: {rel_path}")
        return rel_path

    @classmethod
    def _load_config(cls):
        with cls._lock:
            if cls._config_data is None:
                if cls._config_path is None:
                    cls._config_path = cls._get_config_path()
                with open(cls._config_path, 'r', encoding='utf-8') as f:
                    cls._config_data = json.load(f)

    @classmethod
    def get(cls, key: str, default=None):
        cls._load_config()
        return cls._config_data.get(key, default)

    @classmethod
    def get_section(cls, section: str) -> Dict[str, Any]:
        cls._load_config()
        return cls._config_data.get(section, {})

    @classmethod
    def reload(cls):
        with cls._lock:
            cls._config_data = None
            cls._config_path = None
            cls._load_config()

    @classmethod
    def set(cls, key: str, value: Any):
        cls._load_config()
        with cls._lock:
            cls._config_data[key] = value
            with open(cls._config_path, 'w', encoding='utf-8') as f:
                json.dump(cls._config_data, f, indent=4, ensure_ascii=False)

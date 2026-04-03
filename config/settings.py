import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".llama-agentic"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "provider": "ollama",
    "model": "llama3.2",
    "theme": "dark",
    "ollama_url": "http://localhost:11434",
    "api_keys": {},
    "auto_detect_ollama": True,
    "show_token_usage": True,
    "confirm_destructive": True,
    "working_directory": "."
}

def load_config() -> dict:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            return {**DEFAULT_CONFIG, **config}
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: dict):
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get(key, default=None):
    config = load_config()
    return config.get(key, default)

def set_val(key, value):
    config = load_config()
    config[key] = value
    save_config(config)

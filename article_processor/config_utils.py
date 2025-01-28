# article_processor/config_utils.py
import yaml
import os

def load_config(config_path="config.yaml"):
    """Loads configuration from a YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def get_api_key(config) -> str:
    """Gets the API key from the secrets file specified in config"""
    secrets_path = config.get("secrets_file", "secrets.yaml")
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Secrets file (API Key) not found: {secrets_path}")
    with open(secrets_path, 'r') as f:
        secrets = yaml.safe_load(f)
    api_key = secrets.get("api_key")
    if not api_key:
        raise ValueError("api_key not found in secrets file.")
    return api_key
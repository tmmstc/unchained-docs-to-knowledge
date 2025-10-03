"""
Tests for the LLM settings configuration module.
"""

import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from unittest.mock import patch


def validate_base_url(url):
    """Validate that the base URL is a valid HTTP/HTTPS URL."""
    if not url:
        return False, "Base URL cannot be empty"

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        if result.scheme not in ["http", "https"]:
            return False, "URL must use http or https protocol"
        return True, ""
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def test_validate_base_url():
    """Test URL validation function."""
    is_valid, msg = validate_base_url("https://api.openai.com/v1")
    assert is_valid is True
    assert msg == ""

    is_valid, msg = validate_base_url("http://localhost:8000")
    assert is_valid is True

    is_valid, msg = validate_base_url("")
    assert is_valid is False
    assert "empty" in msg.lower()

    is_valid, msg = validate_base_url("not-a-url")
    assert is_valid is False

    is_valid, msg = validate_base_url("ftp://invalid.com")
    assert is_valid is False
    assert "http" in msg.lower()


def test_config_file_save_and_load():
    """Test saving and loading config to/from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_file = config_dir / "llm_config.json"
        config_dir.mkdir(exist_ok=True)

        test_config = {
            "base_url": "https://api.example.com/v1",
            "api_key": "test-key-123",
            "model": "gpt-4",
        }

        with open(config_file, "w") as f:
            json.dump(test_config, f, indent=2)

        assert config_file.exists()

        with open(config_file, "r") as f:
            loaded_config = json.load(f)

        assert loaded_config == test_config
        assert loaded_config["base_url"] == "https://api.example.com/v1"
        assert loaded_config["api_key"] == "test-key-123"
        assert loaded_config["model"] == "gpt-4"


def test_summarizer_loads_config():
    """Test that summarizer can load config from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_file = config_dir / "llm_config.json"
        config_dir.mkdir(exist_ok=True)

        test_config = {
            "base_url": "https://custom.api.com/v1",
            "api_key": "custom-key",
            "model": "custom-model",
        }

        with open(config_file, "w") as f:
            json.dump(test_config, f)

        with patch("app.summarizer.CONFIG_FILE", config_file):
            from app.summarizer import load_llm_config

            loaded = load_llm_config()
            assert loaded["base_url"] == "https://custom.api.com/v1"
            assert loaded["api_key"] == "custom-key"
            assert loaded["model"] == "custom-model"

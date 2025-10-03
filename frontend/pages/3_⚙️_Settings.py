#!/usr/bin/env python3
"""
Settings Page - Configure LLM API settings for document summarization.
"""

import streamlit as st
import json
from pathlib import Path
from urllib.parse import urlparse


CONFIG_DIR = Path("config")
CONFIG_FILE = CONFIG_DIR / "llm_config.json"


def load_config():
    """Load LLM configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading config: {e}")
            return {}
    return {}


def save_config(config):
    """Save LLM configuration to file."""
    CONFIG_DIR.mkdir(exist_ok=True)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving config: {e}")
        return False


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


def init_session_state():
    """Initialize session state with config values."""
    if "llm_config_loaded" not in st.session_state:
        config = load_config()
        st.session_state.llm_base_url = config.get(
            "base_url", "https://api.openai.com/v1"
        )
        st.session_state.llm_api_key = config.get("api_key", "")
        st.session_state.llm_model = config.get("model", "gpt-3.5-turbo")
        st.session_state.llm_config_loaded = True


def main():
    st.set_page_config(
        page_title="Settings - PDF OCR Processor",
        page_icon="⚙️",
        layout="wide",
    )

    st.title("⚙️ Settings")
    st.markdown("Configure LLM API settings for document summarization")

    init_session_state()

    st.markdown("---")

    with st.form("llm_settings_form"):
        st.subheader("LLM API Configuration")

        base_url = st.text_input(
            "Base URL",
            value=st.session_state.llm_base_url,
            placeholder="https://api.openai.com/v1",
            help=(
                "OpenAI-compatible API base URL "
                "(e.g., https://api.openai.com/v1)"
            ),
        )

        api_key = st.text_input(
            "API Key",
            value=st.session_state.llm_api_key,
            type="password",
            placeholder="sk-...",
            help="Your API key for authentication",
        )

        model = st.text_input(
            "Model Name",
            value=st.session_state.llm_model,
            placeholder="gpt-3.5-turbo",
            help="Model name to use for summarization",
        )

        st.markdown("---")

        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button(
                "💾 Save Settings", type="primary"
            )

        if submit_button:
            is_valid, error_msg = validate_base_url(base_url)

            if not is_valid:
                st.error(f"❌ Validation failed: {error_msg}")
            else:
                config = {
                    "base_url": base_url.strip(),
                    "api_key": api_key.strip(),
                    "model": (
                        model.strip() if model.strip() else "gpt-3.5-turbo"
                    ),
                }

                if save_config(config):
                    st.session_state.llm_base_url = config["base_url"]
                    st.session_state.llm_api_key = config["api_key"]
                    st.session_state.llm_model = config["model"]
                    st.success("✅ Settings saved successfully!")
                else:
                    st.error("❌ Failed to save settings")

    st.markdown("---")
    st.markdown("### Current Configuration")
    api_key_display = (
        '*' * 10 if st.session_state.llm_api_key else '(not set)'
    )
    st.info(
        f"**Base URL:** {st.session_state.llm_base_url}\n\n"
        f"**API Key:** {api_key_display}\n\n"
        f"**Model:** {st.session_state.llm_model}"
    )


if __name__ == "__main__":
    main()

"""
Configuration management module.
Loads settings from config.yaml with env var overrides.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def load_config() -> dict:
    """Load configuration from YAML file with environment variable overrides."""
    with open(_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Allow env var overrides
    if os.getenv("GEMINI_MODEL"):
        config["gemini"]["model"] = os.getenv("GEMINI_MODEL")
    if os.getenv("MAX_OUTPUT_TOKENS"):
        config["gemini"]["max_output_tokens"] = int(os.getenv("MAX_OUTPUT_TOKENS"))
    if os.getenv("LOG_LEVEL"):
        config["logging"]["level"] = os.getenv("LOG_LEVEL")

    return config


def get_api_key() -> str:
    """Retrieve Gemini API key from environment variables only (never hardcoded)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it in your .env file or system environment."
        )
    return api_key

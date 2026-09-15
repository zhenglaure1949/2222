"""Secure, environment-backed application configuration."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

from dotenv import load_dotenv


_PLACEHOLDER_MARKERS = ("your_", "change_me", "replace_me", "example")


def _optional_secret(name: str) -> Optional[str]:
    """Return a configured secret without accepting documented placeholders."""
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if any(marker in value.lower() for marker in _PLACEHOLDER_MARKERS):
        raise ValueError(f"{name} still contains a placeholder value")
    return value


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean")


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    value = default if raw is None else int(raw)
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _api_base(value: str) -> str:
    """Accept credential-free HTTPS endpoints (or HTTP on loopback only)."""
    normalized = value.strip().rstrip("/")
    parsed = urlsplit(normalized)
    if not parsed.hostname or parsed.scheme not in {"http", "https"}:
        raise ValueError("OPENAI_API_BASE must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("OPENAI_API_BASE must not contain credentials, query parameters, or fragments")
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("OPENAI_API_BASE must use HTTPS except on loopback")
    return normalized


class Config:
    """Load trusted process environment first, with local ``.env`` as fallback."""

    def __init__(self, env_file: Optional[str] = None) -> None:
        dotenv_path = Path(env_file) if env_file else Path.cwd() / ".env"
        load_dotenv(dotenv_path=dotenv_path, override=False)

        self.openai_api_key = _optional_secret("OPENAI_API_KEY")
        self.ncbi_api_key = _optional_secret("NCBI_API_KEY")
        self.baidu_appid = _optional_secret("BAIDU_APPID")
        self.baidu_secret_key = _optional_secret("BAIDU_SECRET_KEY")
        self.google_translate_api_key = _optional_secret("GOOGLE_TRANSLATE_API_KEY")

        self.openai_api_base = _api_base(os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.ncbi_email = os.getenv("NCBI_EMAIL")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./medical_agent.db")
        self.cache_enabled = _env_bool("CACHE_ENABLED", True)
        self.cache_ttl = _env_int("CACHE_TTL", 3600)
        self.cache_dir = os.getenv("CACHE_DIR", "./data/cache")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "./logs/agent.log")
        self.max_results = _env_int("MAX_RESULTS", 100)
        self.timeout = _env_int("TIMEOUT", 30)
        self.kb_path = os.getenv("KB_PATH", "./knowledge_base")

    def require_secret(self, name: str) -> str:
        """Return a configured secret or fail closed with a non-secret error."""
        attributes = {
            "OPENAI_API_KEY": "openai_api_key",
            "NCBI_API_KEY": "ncbi_api_key",
            "BAIDU_APPID": "baidu_appid",
            "BAIDU_SECRET_KEY": "baidu_secret_key",
            "GOOGLE_TRANSLATE_API_KEY": "google_translate_api_key",
        }
        attribute = attributes.get(name)
        if attribute is None:
            raise KeyError(f"Unknown secret setting: {name}")
        value = getattr(self, attribute)
        if not value:
            raise RuntimeError(f"Required credential {name} is not configured")
        return value

    def get_all(self) -> Dict[str, Any]:
        """Return diagnostics with credential presence only, never secret values."""
        return {
            "OPENAI_API_KEY_CONFIGURED": bool(self.openai_api_key),
            "NCBI_API_KEY_CONFIGURED": bool(self.ncbi_api_key),
            "BAIDU_APPID_CONFIGURED": bool(self.baidu_appid),
            "BAIDU_SECRET_KEY_CONFIGURED": bool(self.baidu_secret_key),
            "GOOGLE_TRANSLATE_API_KEY_CONFIGURED": bool(self.google_translate_api_key),
            "OPENAI_API_BASE_HOST": urlsplit(self.openai_api_base).hostname,
            "OPENAI_MODEL": self.openai_model,
            "CACHE_ENABLED": self.cache_enabled,
            "CACHE_TTL": self.cache_ttl,
            "MAX_RESULTS": self.max_results,
            "TIMEOUT": self.timeout,
            "KB_PATH": self.kb_path,
        }


_config: Optional[Config] = None


def get_config() -> Config:
    """Return the process-wide configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_logger(name: str) -> logging.Logger:
    """Create a logger without ever interpolating configuration secrets."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return logging.getLogger(name)

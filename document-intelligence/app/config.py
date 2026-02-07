"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "Document Intelligence"
    app_version: str = "1.0.0"
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "25"))
    default_api_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

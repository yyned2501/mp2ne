from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from core.logger import logger


def _load_dotenv_if_present() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv_if_present()


@dataclass(frozen=True)
class Settings:
    nextemby_host: str = os.getenv("NEXTEMBY_HOST", "https://nf.js.248226785.xyz:8443")
    nextemby_api_key: str = os.getenv("NEXTEMBY_API_KEY", "")
    allow_any_bearer: bool = os.getenv("MP2NE_ALLOW_ANY_BEARER", "1") != "0"
    debug_logging: bool = os.getenv("MP2NE_DEBUG_LOGGING", "1") != "0"
    request_timeout_seconds: float = float(os.getenv("MP2NE_TIMEOUT_SECONDS", "15"))
    post_timeout_seconds: float = float(os.getenv("MP2NE_POST_TIMEOUT_SECONDS", "10"))


settings = Settings()

__all__ = ["Settings", "settings"]

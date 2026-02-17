from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_temperature: float
    max_log_chars: int
    timeout_seconds: int
    log_level: str
    mock_mode: bool

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip(),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini").strip(),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            max_log_chars=int(os.getenv("K8S_AI_MAX_LOG_CHARS", "12000")),
            timeout_seconds=int(os.getenv("K8S_AI_TIMEOUT_SECONDS", "30")),
            log_level=os.getenv("K8S_AI_LOG_LEVEL", "INFO").upper().strip(),
            mock_mode=_get_bool("K8S_AI_MOCK_MODE", False),
        )

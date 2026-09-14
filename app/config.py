"""Explicit application configuration; secrets never reach the browser."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings. Demo is deliberately the default."""
    mode: str = os.getenv("APP_MODE", "demo")
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    provider: str = os.getenv("AI_PROVIDER", "openai")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")
    answer_model: str = os.getenv("ANSWER_MODEL", "")
    rate_limit: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "12"))
    daily_limit: int = int(os.getenv("LIVE_REQUESTS_PER_DAY", "100"))

    def __post_init__(self):
        if self.provider not in {"openai", "gemini"}:
            raise ValueError("AI_PROVIDER must be openai or gemini")
        defaults = ("gemini-embedding-001", "gemini-3.6-flash") if self.provider == "gemini" else ("text-embedding-3-small", "gpt-4.1-mini")
        if not self.embedding_model:
            object.__setattr__(self, "embedding_model", defaults[0])
        if not self.answer_model:
            object.__setattr__(self, "answer_model", defaults[1])

    @property
    def provider_key(self):
        return self.gemini_api_key if self.provider == "gemini" else self.api_key

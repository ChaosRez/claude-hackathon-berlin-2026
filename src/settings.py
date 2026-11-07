"""All config in one place. Values come from `.env` (see `.env.example`)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5-5"
    max_tokens: int = 4000
    temperature: float = 0.0

    data_path: Path = ROOT / "dataset" / "finance-filtered.jsonl"
    prompt_version: str = "v1"  # loads prompts/extract_<version>_{system,user}.txt
    mock_llm: bool = False  # True = no API call, return the GUIDE.md example graph


@lru_cache
def get_settings() -> Settings:
    return Settings()

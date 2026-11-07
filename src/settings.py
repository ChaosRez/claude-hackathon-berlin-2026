"""App settings, read from .env (see .env.example). Defaults match src/extract.py."""
import os
from dataclasses import dataclass
from pathlib import Path

from src.extract import load_dotenv
from src.schema import ROOT


@dataclass(frozen=True)
class Settings:
    backend: str  # "api" (needs ANTHROPIC_API_KEY) or "cli" (Claude Code login)
    model: str
    effort: str
    retries: int
    data_path: Path
    prompt_path: Path
    output_dir: Path  # extracted graphs are saved here as <id>.yaml


def get_settings() -> Settings:
    load_dotenv()
    env = os.environ.get
    backend = env("EXTRACT_BACKEND", "auto")
    if backend == "auto":
        backend = "api" if env("ANTHROPIC_API_KEY") or env("ANTHROPIC_AUTH_TOKEN") else "cli"
    return Settings(
        backend=backend,
        model=env("CLAUDE_MODEL", "claude-opus-5-5"),
        effort=env("EFFORT", "high"),
        retries=int(env("RETRIES", "1")),
        data_path=ROOT / env("DATA_PATH", "data/finance-filtered.jsonl"),
        prompt_path=ROOT / env("PROMPT_PATH", "prompts/extract_v2.md"),
        output_dir=ROOT / env("OUTPUT_DIR", "results/app"),
    )

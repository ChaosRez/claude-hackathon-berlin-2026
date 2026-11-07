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
    approach: str  # "voted" (team default, ADR 0001) or "one-pass"
    votes: int  # label samples per answer, voted approach only
    data_path: Path
    prompt_path: Path  # one-pass prompt
    split_prompt: Path  # voted: step 1, cut the answer into pieces
    label_prompt: Path  # voted: step 2, label the pieces (run `votes` times)
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
        approach=env("APPROACH", "voted"),
        votes=int(env("VOTES", "5")),
        data_path=ROOT / env("DATA_PATH", "data/finance-filtered.jsonl"),
        prompt_path=ROOT / env("PROMPT_PATH", "prompts/extract_v2.md"),
        split_prompt=ROOT / env("SPLIT_PROMPT", "prompts/segment_v1.md"),
        label_prompt=ROOT / env("LABEL_PROMPT", "prompts/label_v1.md"),
        output_dir=ROOT / env("OUTPUT_DIR", "results/app"),
    )

"""Step 2: one text -> graph JSON (nodes + edges, format in GUIDE.md), using Claude.

The prompt content is owned by the teammates. Edit the files in `prompts/`,
not this code. Placeholders in the prompt files: {question}, {text}, {guide}.
"""

import json
import re

from anthropic import Anthropic

from src.settings import ROOT, Settings

# The worked example from GUIDE.md section 5. Used when MOCK_LLM=true,
# so the UI, validate and draw can be built without spending API credit.
MOCK_GRAPH = {
    "nodes": [
        {"id": 1, "type": "claim", "text": "In most cases, investing is the better choice.", "main": True},
        {"id": 2, "type": "reason", "text": "Stocks have historically returned more than typical mortgage rates."},
        {"id": 3, "type": "refutation", "text": "However, paying off the loan is a risk-free return."},
        {"id": 4, "type": "rebuttal", "text": "That matters less when your rate is low."},
        {"id": 5, "type": "condition", "text": "If your rate is above 6%, paying it off can make sense."},
        {"id": 6, "type": "recommendation", "text": "So check your rate before you decide."},
    ],
    "edges": [
        {"from": 2, "to": 1, "type": "supports"},
        {"from": 3, "to": 1, "type": "attacks"},
        {"from": 4, "to": 3, "type": "answers"},
        {"from": 5, "to": 1, "type": "qualifies"},
        {"from": 6, "to": 5, "type": "concludes"},
    ],
}


def load_prompts(version: str) -> tuple[str, str]:
    prompts = ROOT / "prompts"
    system = (prompts / f"extract_{version}_system.txt").read_text()
    user = (prompts / f"extract_{version}_user.txt").read_text()
    return system, user


def build_user_prompt(template: str, question: str, text: str) -> str:
    # str.replace, not str.format: the prompt will contain JSON braces.
    guide = (ROOT / "GUIDE.md").read_text() if (ROOT / "GUIDE.md").exists() else ""
    return template.replace("{question}", question).replace("{text}", text).replace("{guide}", guide)


def parse_json(raw: str) -> dict:
    """Take the first {...} block from the reply (tolerates ```json fences)."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object in model reply: {raw[:200]!r}")
    return json.loads(match.group(0))


def extract(question: str, text: str, settings: Settings) -> dict:
    """Return {"nodes": [...], "edges": [...], "raw": <model reply>}."""
    if settings.mock_llm:
        return {**MOCK_GRAPH, "raw": "(mock)"}

    system, user_template = load_prompts(settings.prompt_version)
    client = Anthropic(api_key=settings.anthropic_api_key or None)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        system=system,
        messages=[{"role": "user", "content": build_user_prompt(user_template, question, text)}],
    )
    raw = response.content[0].text
    return {**parse_json(raw), "raw": raw}

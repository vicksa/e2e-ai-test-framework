"""Optional LLM-assisted normalization of free-form scenario descriptions.

The rule-based parser in scenario.py only understands one action per line in
a fixed grammar. This module lets a user describe a scenario in loose prose
(e.g. "log in with valid credentials and check the welcome message") and
have an LLM rewrite it into that grammar before parsing.

This is entirely optional: if ANTHROPIC_API_KEY is not set, generate() below
falls back to returning the input unchanged, so the rest of the pipeline
still works offline with the fixed-grammar format.
"""
from __future__ import annotations

import os

_SYSTEM_PROMPT = """You rewrite a plain-language UI test scenario into a strict \
line-per-action format. Each line must be one of:
Visit "<url>"
Fill in "<field label>" with "<value>"
Click "<button text>"
Expect to see "<text>"
Expect the url to contain "<text>"

Output only the rewritten lines, nothing else."""


def is_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def normalize(scenario_text: str, model: str = "claude-sonnet-5") -> str:
    """Rewrite free-form scenario text into the fixed step grammar.

    Falls back to returning the input unchanged when no API key is
    configured, so callers can always run parse() on the result.
    """
    if not is_available():
        return scenario_text

    import anthropic  # imported lazily so the package works without the SDK installed

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": scenario_text}],
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )

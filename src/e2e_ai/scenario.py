"""Parses a plain-language test scenario into a list of structured Steps.

Scenarios are written as one action per line, e.g.:

    Visit "/login"
    Fill in "Username" with "victoria"
    Fill in "Password" with "secret123"
    Click "Login"
    Expect to see "Welcome, victoria"

This rule-based parser covers a small, explicit grammar rather than trying
to understand arbitrary prose. It's intentionally simple: swap `parse` for
a call to an LLM (see llm_backend.py) if you need to handle free-form
scenario descriptions instead of this line-per-action format.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


class ScenarioParseError(ValueError):
    pass


@dataclass
class Step:
    action: str  # visit | fill | click | expect_text | expect_url
    args: dict


_QUOTED = r'(?:"([^"]*)"|\'([^\']*)\')'

_PATTERNS: list[tuple[str, re.Pattern, callable]] = [
    (
        "visit",
        re.compile(rf"^(?:visit|go to|navigate to)\s+{_QUOTED}$", re.I),
        lambda m: {"url": m.group(1) or m.group(2)},
    ),
    (
        "fill",
        re.compile(rf"^fill(?:\s+in)?\s+{_QUOTED}\s+with\s+{_QUOTED}$", re.I),
        lambda m: {"field": m.group(1) or m.group(2), "value": m.group(3) or m.group(4)},
    ),
    (
        "click",
        re.compile(rf"^click\s+{_QUOTED}$", re.I),
        lambda m: {"target": m.group(1) or m.group(2)},
    ),
    (
        "expect_text",
        re.compile(rf"^expect(?:\s+to)?\s+see\s+{_QUOTED}$", re.I),
        lambda m: {"text": m.group(1) or m.group(2)},
    ),
    (
        "expect_url",
        re.compile(rf"^expect(?:\s+the)?\s+url\s+to\s+(?:be|contain)\s+{_QUOTED}$", re.I),
        lambda m: {"url": m.group(1) or m.group(2)},
    ),
]


def parse_line(line: str, line_no: int) -> Step:
    for action, pattern, extractor in _PATTERNS:
        m = pattern.match(line)
        if m:
            return Step(action=action, args=extractor(m))
    raise ScenarioParseError(
        f"line {line_no}: could not parse step: {line!r}. "
        "Supported forms: Visit \"url\", Fill in \"field\" with \"value\", "
        "Click \"target\", Expect to see \"text\", Expect the url to contain \"text\"."
    )


def parse(scenario: str) -> list[Step]:
    steps = []
    for i, raw_line in enumerate(scenario.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        steps.append(parse_line(line, i))
    if not steps:
        raise ScenarioParseError("scenario has no steps")
    return steps

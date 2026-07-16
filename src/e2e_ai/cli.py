"""Command-line interface for e2e-ai-test-framework.

Usage:
    e2e-ai generate scenario.txt --out generated_tests/test_login.py --name login
"""
from __future__ import annotations

import argparse
import sys

from .codegen import generate_test_file
from .llm_backend import is_available, normalize
from .scenario import ScenarioParseError, parse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="e2e-ai")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Generate a Playwright test from a scenario file")
    generate.add_argument("scenario_file", help="Path to a plain-text scenario description")
    generate.add_argument("--out", required=True, help="Path to write the generated test file")
    generate.add_argument("--name", required=True, help="Test function name suffix (test_<name>)")
    generate.add_argument(
        "--llm",
        action="store_true",
        help="Use an LLM to normalize free-form prose into the step grammar first "
        "(requires ANTHROPIC_API_KEY; falls back to raw parsing if unset)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        with open(args.scenario_file, encoding="utf-8") as fh:
            scenario_text = fh.read()

        if args.llm:
            if not is_available():
                print("warning: --llm requested but ANTHROPIC_API_KEY is not set; "
                      "parsing scenario as-is", file=sys.stderr)
            scenario_text = normalize(scenario_text)

        try:
            steps = parse(scenario_text)
        except ScenarioParseError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        code = generate_test_file(args.name, steps)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(code)

        print(f"Generated {len(steps)} step(s) -> {args.out}")
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

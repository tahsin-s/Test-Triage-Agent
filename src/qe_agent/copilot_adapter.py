from __future__ import annotations

import argparse
import re
from typing import Any


def _find_path(text: str, keyword: str) -> str | None:
    pattern = re.compile(rf"([A-Za-z0-9_./-]*{keyword}(?:[A-Za-z0-9_./-]+)?)", re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


def build_cli_args_from_prompt(prompt: str) -> dict[str, Any]:
    """Convert a chat prompt into the bounded CLI arguments used by the repo-local workflow.

    The contract is intentionally light: parse the most prominent report path, the feature directory,
    and a few simple flags such as dry-run. This keeps the IDE adapter thin and leaves the real
    suite execution to the CLI-first implementation.
    """
    normalized = (prompt or "").strip()
    report_path = _find_path(normalized, "report")
    if report_path and ".json" not in report_path:
        report_path = None

    feature_dir = _find_path(normalized, "features")
    if feature_dir and not feature_dir.startswith(".") and "/features" not in feature_dir:
        feature_dir = None

    if feature_dir and "/" not in feature_dir:
        feature_dir = None

    dry_run = "dry run" in normalized.lower() or "dry-run" in normalized.lower()
    max_tags = 10
    match = re.search(r"max[- ]tags\s+(\d+)", normalized, re.IGNORECASE)
    if match:
        max_tags = int(match.group(1))

    args: dict[str, Any] = {"dry_run": dry_run, "max_tags": max_tags}
    if report_path:
        args["report_path"] = report_path
    if feature_dir:
        args["feature_dir"] = feature_dir
    return args


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate a Copilot chat prompt into repo-local CLI arguments.")
    parser.add_argument("prompt", help="Prompt text to parse")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    print(build_cli_args_from_prompt(args.prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.recommendation.plan_run import plan_run
from qe_agent.recommendation.read_report import read_risk_factors, load_report
from qe_agent.recommendation.score_tags import score_tags

DEFAULT_TAGS: list[str] = []


def _load_descriptions(descriptions_input: str | Path | dict[str, Any] | None) -> list[str]:
    if descriptions_input is None:
        return DEFAULT_TAGS

    if isinstance(descriptions_input, dict):
        return [str(tag) for tag in descriptions_input.keys()]

    path = Path(descriptions_input)
    if not path.exists():
        return DEFAULT_TAGS

    text = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return [str(tag) for tag in parsed.keys()]
    except json.JSONDecodeError:
        pass

    tags: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" in stripped:
            tag, _ = stripped.split(":", 1)
            tag = tag.strip()
        else:
            tag = stripped
        if tag:
            tags.append(tag)
    return tags or DEFAULT_TAGS


def build_tag_plan(
    report_input: str | Path | dict[str, Any],
    descriptions_input: str | Path | dict[str, Any] | None = None,
    max_tags: int = 10,
) -> dict[str, Any]:
    report = load_report(report_input)
    preferred_tags = _load_descriptions(descriptions_input)
    risk_items = read_risk_factors(report)
    scored = score_tags(risk_items, preferred_tags=preferred_tags)
    tags = plan_run(scored, max_tags=max_tags)
    return {
        "status": str(report.get("status") or "UNKNOWN").upper(),
        "summary": str(report.get("summary") or "No summary available."),
        "tags": tags,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recommend an ordered tag run plan from a previous-day report.")
    parser.add_argument("--report", required=True, help="Path to a report JSON file or a report directory")
    parser.add_argument("--descriptions", help="Optional JSON/text file containing tag descriptions")
    parser.add_argument("--output", help="Optional output file path for the tag plan JSON")
    parser.add_argument("--max-tags", type=int, default=10, help="Maximum number of tags to include in the plan")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    plan = build_tag_plan(args.report, descriptions_input=args.descriptions, max_tags=args.max_tags)
    payload = json.dumps(plan, indent=2)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

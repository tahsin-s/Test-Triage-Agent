#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_tag_plan(tag_plan_path: str | Path) -> dict[str, Any]:
    path = Path(tag_plan_path)
    if not path.exists():
        raise FileNotFoundError(f"Tag plan not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"tags": payload}
    if not isinstance(payload, dict) or "tags" not in payload:
        raise ValueError("Tag plan must be a JSON object containing a 'tags' list")
    return payload


def resolve_selected_tags(tag_plan_path: str | Path) -> list[str]:
    plan = load_tag_plan(tag_plan_path)
    tags: list[str] = []
    for entry in plan.get("tags", []):
        if isinstance(entry, str):
            tag = entry.strip()
        elif isinstance(entry, dict):
            tag = str(entry.get("tag") or entry.get("name") or "").strip()
        else:
            continue
        if tag:
            tags.append(tag)

    if not tags:
        raise ValueError(f"No tags found in tag plan: {tag_plan_path}")
    return tags


def build_grep_pattern(tags: list[str]) -> str:
    return "|".join(tags)


def run_selected_tests(
    tag_plan_path: str | Path,
    project_dir: str | Path,
    max_tags: int | None = None,
    dry_run: bool = False,
) -> int:
    selected_tags = resolve_selected_tags(tag_plan_path)
    if max_tags is not None:
        selected_tags = selected_tags[:max_tags]
    if not selected_tags:
        raise ValueError("No selected tags available to run")

    project_root = Path(project_dir)
    if not project_root.exists():
        raise FileNotFoundError(f"Playwright project directory not found: {project_root}")

    results: list[dict[str, Any]] = []
    for index, tag in enumerate(selected_tags, start=1):
        target = tag.strip()
        command = ["npx", "playwright", "test", "--grep", target]
        print(f"[{index}/{len(selected_tags)}] Running {target}")
        if dry_run:
            print("DRY RUN:", " ".join(command))
            results.append({"tag": target, "status": "dry-run", "exit_code": 0})
            continue

        completed = subprocess.run(command, cwd=str(project_root), check=False)
        results.append({"tag": target, "status": "pass" if completed.returncode == 0 else "fail", "exit_code": completed.returncode})
        if completed.returncode != 0:
            summary = {
                "status": "FAIL",
                "selected_tags": selected_tags,
                "results": results,
            }
            print(json.dumps(summary, indent=2))
            return completed.returncode

    summary = {
        "status": "PASS",
        "selected_tags": selected_tags,
        "results": results,
    }
    print(json.dumps(summary, indent=2))
    return 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the recommended Playwright BDD tags in order.")
    parser.add_argument("--tag-plan", required=True, help="Path to the JSON tag-plan output from the tag recommender")
    parser.add_argument("--project-dir", required=True, help="Path to the Playwright project directory")
    parser.add_argument("--max-tags", type=int, help="Optional cap on the number of tags to run")
    parser.add_argument("--dry-run", action="store_true", help="Preview the selected tags without executing Playwright")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        return run_selected_tests(
            tag_plan_path=args.tag_plan,
            project_dir=args.project_dir,
            max_tags=args.max_tags,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

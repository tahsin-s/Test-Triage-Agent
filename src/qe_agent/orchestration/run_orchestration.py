from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.orchestration.run_selected_tests import resolve_selected_tags, run_selected_tests
from qe_agent.orchestration.should_refresh_tags import should_refresh_tags
from qe_agent.tagging.extract_tags import collect_tags


def _default_descriptions_file() -> Path:
    return ROOT / "src" / "qe_agent" / "tagging" / "tag_descriptions.json"


def _write_tags_file(tags: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tags, indent=2), encoding="utf-8")


def _run_command(command: list[str], cwd: str | Path, dry_run: bool = False) -> int:
    if dry_run:
        print("DRY RUN:", " ".join(command))
        return 0

    completed = subprocess.run(command, cwd=str(cwd), check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {completed.returncode}: {' '.join(command)}")
    return completed.returncode


def run_orchestration(
    report_path: str | Path,
    feature_dir: str | Path,
    project_dir: str | Path,
    descriptions_file: str | Path | None = None,
    max_tags: int = 10,
    dry_run: bool = False,
) -> dict[str, Any]:
    report = Path(report_path)
    features = Path(feature_dir)
    project_root = Path(project_dir)
    descriptions = Path(descriptions_file) if descriptions_file else _default_descriptions_file()

    if not report.exists():
        raise FileNotFoundError(f"Report not found: {report}")
    if not features.exists():
        raise FileNotFoundError(f"Feature directory not found: {features}")
    if not project_root.exists() and not dry_run:
        raise FileNotFoundError(f"Playwright project directory not found: {project_root}")

    tags = collect_tags(features)
    if not tags:
        raise ValueError(f"No tags found in feature directory: {features}")

    output_dir = ROOT / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    tags_file = output_dir / "tags.json"
    tag_plan_path = output_dir / "tag_plan.json"

    if should_refresh_tags(descriptions, tags):
        _write_tags_file(tags, tags_file)
        command = [
            sys.executable,
            str(ROOT / "src" / "qe_agent" / "tag_describer.py"),
            "--tags-file",
            str(tags_file),
            "--descriptions-file",
            str(descriptions),
        ]
        _run_command(command, ROOT, dry_run=dry_run)

    command = [
        sys.executable,
        str(ROOT / "src" / "qe_agent" / "tag_recommender.py"),
        "--report",
        str(report),
        "--descriptions",
        str(descriptions),
        "--output",
        str(tag_plan_path),
        "--max-tags",
        str(max_tags),
    ]
    _run_command(command, ROOT, dry_run=dry_run)
    if dry_run and not tag_plan_path.exists():
        tag_plan_path.parent.mkdir(parents=True, exist_ok=True)
        tag_plan_path.write_text(
            json.dumps({
                "status": "FAIL",
                "tags": [{"tag": tag} for tag in tags[:max_tags]],
            }),
            encoding="utf-8",
        )

    exit_code = run_selected_tests(tag_plan_path, project_root, max_tags=max_tags, dry_run=dry_run)
    selected_tags = resolve_selected_tags(tag_plan_path)
    result = {
        "status": "PASS" if exit_code == 0 else "FAIL",
        "report": str(report),
        "feature_dir": str(features),
        "descriptions_file": str(descriptions),
        "tag_plan": str(tag_plan_path),
        "selected_tags": selected_tags,
    }
    print(json.dumps(result, indent=2))
    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh descriptions only when needed, recommend tags, and run the matching Playwright set.")
    parser.add_argument("--report", required=True, help="Path to the JSON report summary")
    parser.add_argument("--feature-dir", required=True, help="Playwright feature directory containing .feature files")
    parser.add_argument("--project-dir", required=True, help="Playwright project directory")
    parser.add_argument("--descriptions-file", default=str(_default_descriptions_file()), help="Existing JSON registry of tag descriptions")
    parser.add_argument("--max-tags", type=int, default=10, help="Maximum number of actionable tags to run")
    parser.add_argument("--dry-run", action="store_true", help="Preview the orchestration without executing Playwright")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        run_orchestration(
            report_path=args.report,
            feature_dir=args.feature_dir,
            project_dir=args.project_dir,
            descriptions_file=args.descriptions_file,
            max_tags=args.max_tags,
            dry_run=args.dry_run,
        )
        return 0
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

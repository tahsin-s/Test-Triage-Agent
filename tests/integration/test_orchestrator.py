import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.copilot_adapter import build_cli_args_from_prompt
from qe_agent.orchestration.run_orchestration import run_orchestration
from qe_agent.orchestration.run_selected_tests import (
    build_grep_pattern,
    resolve_selected_tags,
    run_selected_tests,
)
from qe_agent.orchestration.should_refresh_tags import should_refresh_tags


def test_resolve_selected_tags_and_build_grep_pattern(tmp_path):
    plan_path = tmp_path / "tag-plan.json"
    plan_path.write_text(
        json.dumps({
            "status": "FAIL",
            "tags": [
                {"order": 1, "tag": "@alpha"},
                {"order": 2, "tag": "@beta"},
                {"order": 3, "tag": "@gamma"},
            ],
        }),
        encoding="utf-8",
    )

    tags = resolve_selected_tags(plan_path)

    assert tags == ["@alpha", "@beta", "@gamma"]
    assert build_grep_pattern(tags) == "@alpha|@beta|@gamma"


def test_run_selected_tests_in_dry_run_mode(tmp_path, capsys):
    plan_path = tmp_path / "tag-plan.json"
    plan_path.write_text(
        json.dumps({
            "status": "FAIL",
            "tags": [
                {"order": 1, "tag": "@alpha"},
                {"order": 2, "tag": "@beta"},
            ],
        }),
        encoding="utf-8",
    )

    project_dir = tmp_path / "playwright"
    project_dir.mkdir()

    result = run_selected_tests(plan_path, project_dir, dry_run=True)
    output = capsys.readouterr().out

    assert result == 0
    assert "Running @alpha" in output
    assert "DRY RUN: npx playwright test --grep @alpha" in output
    assert '"status": "PASS"' in output
    assert '"selected_tags": [' in output
    assert '"@alpha"' in output
    assert '"@beta"' in output


def test_should_refresh_tags_when_descriptions_file_is_missing_or_stale(tmp_path):
    descriptions_path = tmp_path / "tag_descriptions.json"

    assert should_refresh_tags(descriptions_path, ["@alpha", "@beta"]) is True

    descriptions_path.write_text(
        json.dumps({"@alpha": "Creates data."}),
        encoding="utf-8",
    )
    assert should_refresh_tags(descriptions_path, ["@alpha", "@beta"]) is True

    descriptions_path.write_text(
        json.dumps({"@alpha": "Creates data.", "@beta": "Smoke test."}),
        encoding="utf-8",
    )
    assert should_refresh_tags(descriptions_path, ["@alpha", "@beta"]) is False


def test_run_orchestration_uses_tag_describer_only_when_needed(tmp_path, capsys):
    report_path = tmp_path / "ai-report.json"
    feature_dir = tmp_path / "features"
    feature_dir.mkdir()
    (feature_dir / "sample.feature").write_text(
        "Feature: Sample\n@alpha\n@beta\nScenario: Rerun\n  Given a step\n",
        encoding="utf-8",
    )
    report_path.write_text(json.dumps({"status": "FAIL", "summary": "Known regression"}), encoding="utf-8")
    descriptions_path = tmp_path / "tag_descriptions.json"
    descriptions_path.write_text(
        json.dumps({"@alpha": "Creates data.", "@beta": "Smoke test."}),
        encoding="utf-8",
    )

    result = run_orchestration(
        report_path=report_path,
        feature_dir=feature_dir,
        project_dir=tmp_path / "playwright",
        descriptions_file=descriptions_path,
        dry_run=True,
    )
    output = capsys.readouterr().out

    assert result["status"] == "PASS"
    assert "tag_recommender.py" in output
    assert "tag_describer.py" not in output


def test_build_cli_args_from_prompt_parses_deferred_copilot_contract():
    args = build_cli_args_from_prompt(
        "Run the triage flow for artifacts/ai-report.json and banking-platform-voltio.QA/playwright/tests/bdd/features in dry run"
    )

    assert args["report_path"] == "artifacts/ai-report.json"
    assert args["feature_dir"] == "banking-platform-voltio.QA/playwright/tests/bdd/features"
    assert args["dry_run"] is True

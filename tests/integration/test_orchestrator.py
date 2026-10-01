import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.orchestration.run_selected_tests import build_grep_pattern, resolve_selected_tags


def test_resolve_selected_tags_and_build_grep_pattern(tmp_path):
    plan_path = tmp_path / "tag-plan.json"
    plan_path.write_text(
        json.dumps({
            "status": "FAIL",
            "tags": [
                {"order": 1, "tag": "@CreatesData"},
                {"order": 2, "tag": "@fail"},
                {"order": 3, "tag": "@SmokeTest"},
            ],
        }),
        encoding="utf-8",
    )

    tags = resolve_selected_tags(plan_path)

    assert tags == ["@CreatesData", "@fail", "@SmokeTest"]
    assert build_grep_pattern(tags) == "@CreatesData|@fail|@SmokeTest"

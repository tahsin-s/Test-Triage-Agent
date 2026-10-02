from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tag_recommender import build_tag_plan


def test_build_tag_plan_returns_ordered_tags_and_duration_estimates():
    report = {
        "status": "FAIL",
        "total_tests": 60,
        "failed": 54,
        "duration_seconds": 681,
        "summary": "6 passed / 54 failed in 681s",
        "top_failures": [
            {"title": "Test timeout of 30000ms exceeded.", "location": "tests/bdd/features/auth/registration.feature"},
            {"title": "Test timeout of 30000ms exceeded.", "location": "tests/bdd/features/auth/registration.feature"},
        ],
    }
    descriptions = {
        "@alpha": "A generic scenario tag used in the example.",
        "@beta": "A second generic scenario tag used in the example.",
        "@gamma": "A third generic scenario tag used in the example.",
    }

    plan = build_tag_plan(report, descriptions, max_tags=2)

    assert plan["status"] == "FAIL"
    assert len(plan["tags"]) <= 2
    assert all("tag" in item for item in plan["tags"])
    assert all("estimated_duration_seconds" in item for item in plan["tags"])
    assert [item["order"] for item in plan["tags"]] == [1, 2]
    assert all(item["estimated_duration_seconds"] > 0 for item in plan["tags"])
    assert any(item["tag"] in descriptions for item in plan["tags"])

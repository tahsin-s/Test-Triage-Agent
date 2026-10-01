from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tagging.extract_tags import collect_tags


def test_collect_tags_returns_unique_sorted_tags_from_feature_files():
    feature_dir = ROOT / "banking-platform-voltio.QA" / "playwright" / "tests" / "bdd" / "features"

    tags = collect_tags(feature_dir)

    assert tags == ["@CreatesData", "@SmokeTest", "@fail"]


def test_collect_tags_includes_temp_tags_and_cleans_up_afterward(tmp_path):
    feature_dir = tmp_path / "features"
    feature_dir.mkdir()
    feature_file = feature_dir / "tmp_tags.feature"
    feature_file.write_text(
        "Feature: temp tags\n\n"
        "@Alpha @Beta\n"
        "Scenario: one\n"
        "  Given something\n\n"
        "@Gamma @Delta\n"
        "Scenario: two\n"
        "  Then something else\n",
        encoding="utf-8",
    )

    try:
        tags = collect_tags(feature_dir)
        assert tags == ["@Alpha", "@Beta", "@Delta", "@Gamma"]
    finally:
        feature_file.unlink(missing_ok=True)
        feature_dir.rmdir()

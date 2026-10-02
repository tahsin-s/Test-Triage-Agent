import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tagging.describe_tags import describe_tags


def test_describe_tags_uses_known_descriptions_and_fallback(tmp_path):
    descriptions_file = tmp_path / "tag_descriptions.json"
    descriptions = describe_tags(
        ["@alpha", "@beta", "@gamma", "@unknown-tag"],
        descriptions_file=str(descriptions_file),
    )

    assert descriptions["@alpha"]
    assert descriptions["@beta"]
    assert descriptions["@gamma"]
    assert "@unknown-tag" in descriptions
    assert "unknown tag" in descriptions["@unknown-tag"].lower()
    assert "scenario" in descriptions["@unknown-tag"].lower()


def test_describe_tags_reads_from_file_and_persists_generated_descriptions(tmp_path):
    descriptions_file = tmp_path / "tag_descriptions.json"
    descriptions_file.write_text(json.dumps({"@alpha": "Custom known description."}), encoding="utf-8")

    descriptions = describe_tags(
        ["@alpha", "@new-tag"],
        descriptions_file=str(descriptions_file),
        generator=lambda tag: f"Generated description for {tag}",
    )

    assert descriptions["@alpha"] == "Custom known description."
    assert descriptions["@new-tag"] == "Generated description for @new-tag"

    saved = json.loads(descriptions_file.read_text(encoding="utf-8"))
    assert saved["@alpha"] == "Custom known description."
    assert saved["@new-tag"] == "Generated description for @new-tag"


def test_describe_tags_uses_fallback_when_generation_fails(tmp_path):
    descriptions_file = tmp_path / "tag_descriptions.json"

    descriptions = describe_tags(
        ["@unknown-tag"],
        descriptions_file=str(descriptions_file),
        generator=lambda tag: None,
    )

    assert descriptions["@unknown-tag"].lower().startswith("@unknown-tag has no dedicated description yet")
    saved = json.loads(descriptions_file.read_text(encoding="utf-8"))
    assert saved["@unknown-tag"].lower().startswith("@unknown-tag has no dedicated description yet")

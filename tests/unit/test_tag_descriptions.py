import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tagging.describe_tags import describe_tags


def test_describe_tags_uses_known_descriptions_and_fallback():
    descriptions = describe_tags(["@CreatesData", "@SmokeTest", "@fail", "@UnknownTag"])

    assert descriptions["@CreatesData"] == "Creates the test data required for this scenario."
    assert descriptions["@SmokeTest"] == "Fast smoke check for critical user flows."
    assert descriptions["@fail"] == "Known failing scenario retained to track the regression."
    assert "@UnknownTag" in descriptions
    assert "unknown tag" in descriptions["@UnknownTag"].lower()
    assert "scenario" in descriptions["@UnknownTag"].lower()


def test_describe_tags_reads_from_file_and_persists_generated_descriptions(tmp_path):
    descriptions_file = tmp_path / "tag_descriptions.json"
    descriptions_file.write_text(json.dumps({"@CreatesData": "Custom known description."}), encoding="utf-8")

    descriptions = describe_tags(
        ["@CreatesData", "@NewTag"],
        descriptions_file=str(descriptions_file),
        generator=lambda tag: f"Generated description for {tag}",
    )

    assert descriptions["@CreatesData"] == "Custom known description."
    assert descriptions["@NewTag"] == "Generated description for @NewTag"

    saved = json.loads(descriptions_file.read_text(encoding="utf-8"))
    assert saved["@CreatesData"] == "Custom known description."
    assert saved["@NewTag"] == "Generated description for @NewTag"


def test_describe_tags_uses_fallback_when_generation_fails(tmp_path):
    descriptions_file = tmp_path / "tag_descriptions.json"

    descriptions = describe_tags(
        ["@UnknownTag"],
        descriptions_file=str(descriptions_file),
        generator=lambda tag: None,
    )

    assert descriptions["@UnknownTag"].lower().startswith("@unknowntag has no dedicated description yet")
    saved = json.loads(descriptions_file.read_text(encoding="utf-8"))
    assert saved["@UnknownTag"].lower().startswith("@unknowntag has no dedicated description yet")

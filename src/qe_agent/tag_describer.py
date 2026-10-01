#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tagging.describe_tags import describe_tags


def _load_tags(path: str) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Tags file not found: {path}")

    text = file_path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []

    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    return [line.strip() for line in stripped.splitlines() if line.strip()]


def write_descriptions(
    tags: list[str],
    output_path: str | None = None,
    descriptions_file: str | None = None,
) -> str:
    descriptions = describe_tags(tags, descriptions_file=descriptions_file)
    output = "\n".join(f"{tag}: {description}" for tag, description in descriptions.items())
    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe the purpose of each tag in a one-shot summary.")
    parser.add_argument("--tags-file", required=True, help="Tags file: JSON array or plain text list")
    parser.add_argument("--descriptions-file", help="Optional JSON file used to store known tag descriptions")
    parser.add_argument("--output", help="Optional output file for the human-readable tag descriptions")
    args = parser.parse_args()

    tags = _load_tags(args.tags_file)
    output = write_descriptions(tags, args.output, descriptions_file=args.descriptions_file)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

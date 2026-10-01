#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.tagging.extract_tags import collect_tags


def main() -> int:
    parser = argparse.ArgumentParser(description="List all BDD tags used in the Playwright feature suite.")
    parser.add_argument(
        "--features",
        default=str(ROOT / "banking-platform-voltio.QA" / "playwright" / "tests" / "bdd" / "features"),
        help="Directory containing .feature files",
    )
    parser.add_argument("--json", action="store_true", help="Emit tags as JSON instead of plain text")
    args = parser.parse_args()

    tags = collect_tags(args.features)
    if args.json:
        print(json.dumps(tags))
    else:
        print("\n".join(tags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

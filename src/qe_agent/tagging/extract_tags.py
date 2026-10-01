import re
from pathlib import Path

TAG_PATTERN = re.compile(r'@([A-Za-z0-9_]+)')


def collect_tags(feature_dir: str | Path) -> list[str]:
    feature_path = Path(feature_dir)
    if not feature_path.exists():
        raise FileNotFoundError(f"Feature directory not found: {feature_path}")

    tags = set()
    for feature_file in sorted(feature_path.rglob("*.feature")):
        for line in feature_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not stripped.startswith("@"):
                continue
            for match in TAG_PATTERN.finditer(stripped):
                tags.add(f"@{match.group(1)}")

    return sorted(tags)

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def should_refresh_tags(descriptions_file: str | Path, tags: Iterable[str] | None = None) -> bool:
    """Return True when the existing description registry is missing or stale for a tag set."""
    path = Path(descriptions_file)
    if tags is None:
        tags = []

    if not path.exists():
        return True

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True

    if not isinstance(payload, dict):
        return True

    registry = {
        str(key).strip(): str(value).strip()
        for key, value in payload.items()
        if str(key).strip() and str(value).strip()
    }
    if not registry:
        return True

    missing = [tag for tag in [str(value).strip() for value in tags if str(value).strip()] if tag not in registry]
    return bool(missing)

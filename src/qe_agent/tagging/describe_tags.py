from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

DEFAULT_DESCRIPTIONS_FILE = Path(__file__).with_name("tag_descriptions.json")
FALLBACK_DESCRIPTION = "{tag} has no dedicated description yet; it marks an unknown tag scenario or workflow."


def _fallback_description(tag: str) -> str:
    return FALLBACK_DESCRIPTION.format(tag=tag)


def _load_descriptions_file(path: str | Path | None = None) -> dict[str, str]:
    file_path = Path(path) if path else DEFAULT_DESCRIPTIONS_FILE
    if not file_path.exists():
        return {}

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(payload, dict):
        return {}

    normalized: dict[str, str] = {}
    for raw_tag, raw_value in payload.items():
        tag = str(raw_tag).strip()
        description = str(raw_value).strip()
        if tag and description:
            normalized[tag] = description
    return normalized


def _save_descriptions_file(path: str | Path | None, descriptions: dict[str, str]) -> None:
    file_path = Path(path) if path else DEFAULT_DESCRIPTIONS_FILE
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(descriptions, indent=2, sort_keys=True), encoding="utf-8")


def _generate_tag_description(tag: str) -> str | None:
    if not tag or tag == "@":
        return None

    raw_tag = tag.lstrip("@")
    if not raw_tag:
        return None

    readable = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw_tag)
    readable = readable.replace("-", " ").replace("_", " ")
    readable = " ".join(part for part in readable.split() if part)
    readable = readable.lower().strip()
    if not readable:
        return None

    return f"Marks the {readable} scenario or workflow."


def describe_tags(
    tags: list[str],
    descriptions_file: str | Path | None = None,
    generator: Callable[[str], str | None] | None = None,
) -> dict[str, str]:
    known_registry = _load_descriptions_file(descriptions_file)
    descriptions: dict[str, str] = {}
    generated_any = False

    for tag in tags:
        normalized = tag.strip()
        if not normalized:
            continue

        if normalized in known_registry:
            descriptions[normalized] = known_registry[normalized]
            continue

        description = None
        if generator is not None:
            description = generator(normalized)
        else:
            description = _generate_tag_description(normalized)

        if description and description.strip():
            descriptions[normalized] = description.strip()
            known_registry[normalized] = description.strip()
            generated_any = True
        else:
            fallback = _fallback_description(normalized)
            descriptions[normalized] = fallback
            known_registry[normalized] = fallback
            generated_any = True

    if generated_any:
        _save_descriptions_file(descriptions_file, known_registry)

    return descriptions

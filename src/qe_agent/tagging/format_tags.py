from __future__ import annotations


def format_tags(tags: list[str], as_json: bool = False) -> str:
    if as_json:
        return "\n".join(tags)
    return "\n".join(tags)

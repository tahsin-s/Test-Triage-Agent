from __future__ import annotations

from typing import Any


def plan_run(scored_tags: list[dict[str, Any]], max_tags: int = 10) -> list[dict[str, Any]]:
    ordered = []
    for index, item in enumerate(scored_tags[:max_tags], start=1):
        ordered.append({
            "order": index,
            "tag": item["tag"],
            "priority": item["priority"],
            "estimated_duration_seconds": item["estimated_duration_seconds"],
            "reason": item["reason"],
        })
    return ordered

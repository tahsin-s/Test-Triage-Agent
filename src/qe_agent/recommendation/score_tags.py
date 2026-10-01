from __future__ import annotations

from typing import Any


def score_tags(risk_items: list[dict[str, Any]], preferred_tags: list[str] | None = None) -> list[dict[str, Any]]:
    ordered_tags = preferred_tags or [item.get("tag") for item in risk_items if item.get("tag")]
    tag_scores: list[dict[str, Any]] = []

    for tag in ordered_tags:
        risk_total = sum(item["risk_score"] for item in risk_items if item.get("tag") == tag)
        normalized_name = str(tag).replace("@", "")
        base_score = 30 + min(80, max(10, len(normalized_name) * 5))
        final_priority = base_score + risk_total
        reason = next(
            (item["reason"] for item in risk_items if item.get("tag") == tag),
            f"Keep {tag} in the execution queue to validate the most relevant workflow.",
        )
        estimated_duration = max(30, min(360, int(round(final_priority / 3))))
        tag_scores.append({
            "tag": tag,
            "priority": final_priority,
            "estimated_duration_seconds": estimated_duration,
            "reason": reason,
        })

    return sorted(tag_scores, key=lambda item: (-item["priority"], item["tag"]))

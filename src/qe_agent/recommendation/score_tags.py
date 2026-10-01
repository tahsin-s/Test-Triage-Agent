from __future__ import annotations

from typing import Any


def score_tags(risk_items: list[dict[str, Any]], preferred_tags: list[str] | None = None) -> list[dict[str, Any]]:
    weight_by_tag = {
        "@fail": 120,
        "@CreatesData": 95,
        "@SmokeTest": 80,
    }

    ordered_tags = preferred_tags or list(weight_by_tag)
    tag_scores: list[dict[str, Any]] = []

    for tag in ordered_tags:
        risk_total = sum(item["risk_score"] for item in risk_items if item.get("tag") == tag)
        base_score = weight_by_tag.get(tag, 40)
        final_priority = base_score + risk_total
        reason = next(
            (item["reason"] for item in risk_items if item.get("tag") == tag),
            f"Keep {tag} in the execution queue to validate the most relevant workflow.",
        )
        estimated_duration = max(45, min(360, int(round(final_priority / 3))))
        tag_scores.append({
            "tag": tag,
            "priority": final_priority,
            "estimated_duration_seconds": estimated_duration,
            "reason": reason,
        })

    return sorted(tag_scores, key=lambda item: (-item["priority"], item["tag"]))

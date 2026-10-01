from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_report(report_input: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report_input, dict):
        return report_input

    path = Path(report_input)
    if path.is_dir():
        for candidate in ("ai-report.json", "report.json", "summary.json"):
            candidate_path = path / candidate
            if candidate_path.exists():
                path = candidate_path
                break

    if not path.exists():
        raise FileNotFoundError(f"Report file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def read_risk_factors(report_input: str | Path | dict[str, Any]) -> list[dict[str, Any]]:
    report = load_report(report_input)
    failed = int(report.get("failed") or 0)
    total = int(report.get("total_tests") or 0)
    status = str(report.get("status") or "UNKNOWN").upper()
    top_failures = report.get("top_failures") or []

    if not top_failures and failed == 0:
        return [{
            "tag": "@SmokeTest",
            "risk_score": 25,
            "reason": "No current failures were reported; use a fast smoke pass.",
            "failure_count": 0,
        }]

    risk_items: list[dict[str, Any]] = []
    for failure in top_failures[:5]:
        failure_location = str(failure.get("location") or "unknown")
        failure_title = str(failure.get("title") or failure.get("error") or "Failure")

        if "registration" in failure_location or "account" in failure_location:
            tag = "@CreatesData"
            reason = "Registration/account setup is failing and likely requires fresh data setup."
        elif "auth" in failure_location or "login" in failure_location:
            tag = "@SmokeTest"
            reason = "Authentication is a critical user flow and should be validated early."
        else:
            tag = "@fail"
            reason = "A failing path was reported and should be treated as high-priority regression coverage."

        risk_score = 55 + failed + (5 if status == "FAIL" else 0)
        if total:
            risk_score += max(0, int(round((failed / total) * 20)))

        risk_items.append({
            "tag": tag,
            "risk_score": risk_score,
            "reason": f"{reason} Latest failure: {failure_title}",
            "failure_count": failed,
        })

    if not risk_items:
        risk_items.append({
            "tag": "@SmokeTest",
            "risk_score": 35,
            "reason": "The report shows no detailed failure context, so keep validation shallow and fast.",
            "failure_count": failed,
        })

    return risk_items

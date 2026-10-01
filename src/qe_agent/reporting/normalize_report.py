def normalize_report(data: dict) -> dict:
    """Return a compact JSON payload suitable for AI analysis."""
    total = int(data.get("total_tests") or 0)
    passed = int(data.get("passed") or 0)
    failed = int(data.get("failed") or 0)
    status = str(data.get("status") or ("FAIL" if failed else "PASS")).upper()

    summary = {
        "status": status,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "duration_seconds": int(data.get("duration_seconds") or 0),
        "summary": data.get("summary") or f"{passed} passed / {failed} failed",
        "top_failures": [
            {
                "title": item.get("title", "Unnamed failure"),
                "error": item.get("error", "No error detail captured"),
                "location": item.get("location", "unknown"),
            }
            for item in (data.get("top_failures") or [])[:5]
        ],
    }
    return summary

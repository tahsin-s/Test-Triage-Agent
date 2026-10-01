from pathlib import Path

from qe_agent.reporting.prepare_playwright_output import _read_report_json, build_report_summary


def test_slice_1_summary_matches_the_real_playwright_report():
    report_dir = (
        Path(__file__).resolve().parents[2]
        / "banking-platform-voltio.QA"
        / "playwright"
        / "playwright-report"
    )

    summary = build_report_summary(str(report_dir))
    report_json = _read_report_json(report_dir)
    expected_duration = int(round(float(report_json.get("duration") or 0) / 1000))

    assert summary["status"] == "FAIL"
    assert summary["total_tests"] == 18
    assert summary["passed"] == 9
    assert summary["failed"] == 9
    assert summary["summary"] == f"9 passed / 9 failed in {expected_duration}s"
    assert summary["top_failures"]

    first_failure = summary["top_failures"][0]
    assert "Could not open an account for customer" in first_failure["error"]
    assert "500" in first_failure["error"]

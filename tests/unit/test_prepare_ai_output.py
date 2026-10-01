from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qe_agent.reporting.prepare_playwright_output import build_report_summary


def test_build_report_summary_infers_counts_and_top_failure():
    report_dir = ROOT / "banking-platform-voltio.QA" / "playwright" / "playwright-report"

    summary = build_report_summary(str(report_dir))

    assert summary["status"] == "FAIL"
    assert summary["total_tests"] == 18
    assert summary["passed"] == 9
    assert summary["failed"] == 9
    assert summary["top_failures"]
    assert "Could not open an account for customer" in summary["top_failures"][0]["title"]
    assert "500" in summary["top_failures"][0]["error"]

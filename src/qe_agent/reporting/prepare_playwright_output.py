import argparse
import base64
import io
import json
import re
import zipfile
from pathlib import Path

from qe_agent.reporting.normalize_report import normalize_report

MAX_FAILURES = 5


def _extract_template_payload(html_text: str) -> str:
    pattern = r'<template[^>]+id=["\']playwrightReportBase64["\']>(?:data:application/zip;base64,)?([^<]+)</template>'
    match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Could not find Playwright report payload in index.html")
    return match.group(1).strip()


def _read_report_json(report_dir: Path) -> dict:
    direct = report_dir / "report.json"
    if direct.exists():
        return json.loads(direct.read_text(encoding="utf-8"))

    index_html = report_dir / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"No report.json or index.html found in {report_dir}")

    payload = _extract_template_payload(index_html.read_text(encoding="utf-8"))
    raw = base64.b64decode(payload)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if "report.json" not in archive.namelist():
            raise ValueError("Embedded Playwright archive does not contain report.json")
        return json.loads(archive.read("report.json"))


def _extract_error_text(markdown_text: str) -> str:
    match = re.search(r"# Error details\s*```[a-zA-Z]*\n(.*?)\n```", markdown_text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    error_match = re.search(r"Error:\s*(.*)", markdown_text, flags=re.DOTALL)
    if error_match:
        return error_match.group(1).strip()

    return "Error detail not captured"


def _read_failure_detail(report_dir: Path, test: dict) -> str:
    for result in test.get("results", []):
        for attachment in result.get("attachments", []):
            name = attachment.get("name")
            path_value = attachment.get("path")
            if name != "error-context" or not path_value:
                continue
            attachment_path = report_dir / path_value
            if attachment_path.exists():
                return _extract_error_text(attachment_path.read_text(encoding="utf-8"))
    return test.get("title", "Unnamed failure")


def build_report_summary(report_dir: str) -> dict:
    report_dir_path = Path(report_dir)
    if not report_dir_path.exists():
        raise FileNotFoundError(f"Report directory does not exist: {report_dir}")

    report = _read_report_json(report_dir_path)
    stats = report.get("stats", {})
    total = int(stats.get("total") or 0)
    passed = int(stats.get("expected") or max(0, total - int(stats.get("unexpected") or 0)))
    failed = int(stats.get("unexpected") or max(0, total - passed))
    duration_seconds = max(0, int(round(float(report.get("duration") or 0) / 1000)))

    top_failures = []
    for file_entry in report.get("files", []):
        for test in file_entry.get("tests", []):
            outcome = str(test.get("outcome") or "").lower()
            if outcome == "expected":
                continue
            title = test.get("title") or "Unnamed failure"
            location = test.get("location", {}).get("file", "unknown")
            error = _read_failure_detail(report_dir_path, test)
            first_error_line = error.splitlines()[0].strip() if error else title
            top_failures.append({
                "title": first_error_line,
                "test_title": title,
                "location": location,
                "error": error,
            })
            if len(top_failures) >= MAX_FAILURES:
                break
        if len(top_failures) >= MAX_FAILURES:
            break

    summary_text = (
        f"{passed} passed / {failed} failed in {duration_seconds}s"
        if total or failed or passed
        else "No tests found in the Playwright report"
    )

    result = {
        "status": "FAIL" if failed else "PASS",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "duration_seconds": duration_seconds,
        "summary": summary_text,
        "top_failures": top_failures,
    }
    return normalize_report(result)


def write_report_summary(report_dir: str, output_path: str | None = None, dry_run: bool = False) -> dict:
    summary = build_report_summary(report_dir)
    target = Path(output_path) if output_path else Path(report_dir).parent / "artifacts" / "ai-report.json"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    payload = {
        "status": summary["status"],
        "summary": summary["summary"],
        "artifact": str(target),
        "total_tests": summary["total_tests"],
        "passed": summary["passed"],
        "failed": summary["failed"],
    }
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize a Playwright report into an AI-ready JSON payload.")
    parser.add_argument("--report-dir", required=True, help="Directory containing Playwright report output")
    parser.add_argument("--output", help="Target filepath for the compact JSON summary")
    parser.add_argument("--dry-run", action="store_true", help="Preview the summary without writing a file")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        result = write_report_summary(args.report_dir, args.output, dry_run=args.dry_run)
        print(json.dumps(result, separators=(",", ":")))
        return 0
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"ERROR: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

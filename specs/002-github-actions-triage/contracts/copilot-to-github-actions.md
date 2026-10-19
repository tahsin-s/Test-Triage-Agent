# Contract: Copilot to GitHub Actions

## Purpose

This contract defines the minimal data exchanged between the IDE-side Copilot orchestrator and the remote GitHub Actions execution layer.

## Request format

```json
{
  "branch": "main",
  "repo": "owner/repository",
  "scope": "playwright",
  "tags": [
    { "name": "@smoke", "priority": 1, "reason": "Highest-risk area from prior report" },
    { "name": "@auth", "priority": 2, "reason": "Known failing area" }
  ],
  "max_tags": 2,
  "report_path": "artifacts/ai-report.json",
  "requested_by": "copilot",
  "requested_at": "2026-10-01T00:00:00Z"
}
```

## Validation rules

- `branch` must be a non-empty string.
- `repo` must contain the owner and repository name in `owner/repo` format.
- `tags` must be an ordered list, with the first item executed first.
- `max_tags` must be less than or equal to the workflow cap.
- `report_path` may be absent if the workflow can safely run without a prior report.
- `requested_by` must be set to the orchestration source (`copilot`).

## Response format

```json
{
  "run_id": 12345,
  "status": "queued",
  "workflow": "triage-playwright.yml",
  "branch": "main",
  "tag_count": 2,
  "summary": "Queued ordered Playwright run for selected tags"
}
```

## GitHub Actions requirements

- The workflow must validate the payload before beginning execution.
- It must reject requests with an empty or malformed tag list.
- It must print a compact final summary after completion.
- It must publish the artifact summary in a deterministic format to support the next triage cycle.

## Security and review expectations

- The JSON payload is intentionally small and inspectable.
- Secrets or credentials must never be embedded in the request payload.
- The workflow must fail clearly if the selected branch, repo, or report source is unavailable.

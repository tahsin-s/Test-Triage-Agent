# Research: GitHub Actions QA Triage

## Decision: GitHub Actions becomes the execution authority, not the IDE

The system will treat GitHub Actions as the remote execution environment that owns the Playwright suite, while Copilot remains the orchestration layer that decides which tags to run next. This matches the repo’s existing CLI-first triage flow and keeps the once-strongly-coupled workflow bounded: Copilot fetches artifacts, ranks tags, and sends a compact execution request; GitHub Actions resolves the branch and runs the selected tests in sequence.

### Rationale

- The repo already contains deterministic scripts for tag extraction and report parsing.
- The lifecycle is naturally split: planning in Copilot, execution in GitHub Actions.
- A branch-aware remote workflow is easier to review and audit when the interface is compact and JSON-driven.
- The feature scope explicitly avoids broad autonomous loops; the run is bounded by a tag cap and a single ordered request.

### Alternatives considered

1. Run everything directly from the IDE
   - Rejected because it couples local editor behavior to remote branch execution and reduces traceability.

2. Push the full triage logic into GitHub Actions only
   - Rejected because the developer experience is weaker and branch-specific agent reasoning is harder to inspect in the IDE.

3. Use a database-backed orchestrator
   - Rejected as over-engineered for this bounded proof of concept.

## Decision: Use a compact JSON contract between Copilot and GitHub Actions

The remote workflow will accept a request payload that includes the branch, target tag list, ordering, and optional metadata such as the prior report location. The payload remains intentionally small so a human can inspect it and the workflow can validate it before executing Playwright.

### Example request payload

```json
{
  "branch": "main",
  "target": "playwright",
  "tags": ["@smoke", "@auth", "@goals"],
  "max_tags": 3,
  "report_uri": "https://api.github.com/repos/org/repo/actions/artifacts/...",
  "reasoning": [
    "Highest-risk tags from prior report",
    "Known tag descriptions applied",
    "Execution cap enforced"
  ]
}
```

### Rationale

- Simple enough to be reviewed in a PR or workflow log.
- Easy to generate from a Copilot prompt or script.
- Deterministic enough for a GitHub Action to validate before running tests.

### Alternatives considered

1. Large free-form prompt strings
   - Rejected because it is harder to validate and harder to reason about in automation.

2. Direct shell command injection from the IDE into GitHub Actions
   - Rejected because it bypasses the controlled interface and weakens security controls.

## Decision: GitHub Actions will fetch prior report and tag metadata through deterministic scripts

The remote branch already contains scripts that discover tags and parse the Playwright report. Those scripts remain the source of truth instead of ad hoc parsing logic embedded in the workflow. This ensures the logic is reproducible and easy to test locally before deployment.

### Rationale

- The repo already owns the deterministic logic for tags and reports.
- Consistency between local and remote execution reduces accidental drift.
- The scripts can be called from both CLI and workflow steps without changing behavior.

### Alternatives considered

1. Parse HTML reports in the workflow directly
   - Rejected because it is brittle and less deterministic than the repo’s artifact parser.

2. Re-implement report parsing in GitHub Actions YAML
   - Rejected because it duplicates logic and introduces maintenance cost.

## Decision: Use slice-based progress gates with human-verifiable outputs

Each milestone in the implementation must produce a visible artifact or command output that a developer can run or inspect without guesswork. This makes the integration reviewable in both the IDE and the GitHub UI.

### Slice plan

- Slice 1: repository workflow contract and manual GitHub setup
- Slice 2: branch artifact retrieval and report summary
- Slice 3: tag discovery and description resolution
- Slice 4: ordered tag plan generation
- Slice 5: workflow dispatch and execution
- Slice 6: end-to-end validation and artifact publication

### Rationale

- It keeps development incremental.
- It creates review checkpoints at meaningful milestones.
- It reduces risk by proving each sub-flow before adding the next one.

## Manual GitHub web setup required

The repo may require a small amount of one-time configuration in GitHub before the workflow is fully functional. This is expected and should be treated as a standard setup negotiation, not a code blocker.

Required items:

- Ensure Actions is enabled for the target repository.
- Set workflow permissions to allow reading repository contents and writing workflow run metadata, if the repo policy requires it.
- If the workflow needs private artifacts or a personal access token, add the secret in GitHub Settings > Secrets and variables > Actions.
- Verify the branch is configured to allow workflow runs, and that the default branch is correct for the integration.

## Open questions resolved

- Developer entry point: Copilot in the IDE, not a separate app, by design.
- Remote execution authority: GitHub Actions.
- Data source for tags and reports: deterministic repo scripts plus workflow artifact consumption.
- Execution safety: tag cap + ordered list + single run flow.
- Human verification: each slice must produce a concrete CLI or GitHub-visible result.

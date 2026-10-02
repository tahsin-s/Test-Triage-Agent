# Test Triage Agent

## Objective

This project is a small, bounded Proof of Concept for an agentic QA triage workflow. The goal is to turn a Playwright BDD test run into a compact, human-readable triage plan that helps a developer or QA engineer quickly decide which tags to run next, in what order, and how long they are likely to take.

The workflow is intentionally narrow and reviewable:
- prepare the report into a compact AI-ready summary
- list the available BDD tags
- generate short descriptions for each tag
- rank the tags using the prior day’s report
- run the selected Playwright tags in order

The project is designed to stay easy to run from the command line, with clear boundaries and hard-stop behavior so it does not spiral into a broad autonomous system.

## Repository Layout

- `src/qe_agent/reporting/` - report summarization and normalization
- `src/qe_agent/tagging/` - tag discovery and tag description logic
- `src/qe_agent/recommendation/` - risk analysis and tag ordering
- `src/qe_agent/orchestration/` - execution orchestration for selected Playwright tags
- `scripts/` - CLI wrappers for the functional slices
- `tests/` - unit and integration regressions
- `banking-platform-voltio.QA/playwright/` - the Playwright BDD project used for real automation checks
- `artifacts/` - generated run outputs and summaries

## Slices

### Slice 1: Prepare Playwright Output for an AI

Purpose: Convert raw Playwright output into a compact JSON summary suitable for quick review and downstream triage.

CLI example:

```bash
cd {PROJECT_ROOT}
./.venv/bin/python src/qe_agent/reporting/prepare_playwright_output.py --report-dir ./banking-platform-voltio.QA/playwright/playwright-report --output ./artifacts/ai-report.json
```

This produces a compact summary with:
- overall status
- pass/fail counts
- duration
- top failure indicators

### Slice 2: Output All Available BDD Tags

Purpose: Discover all unique Gherkin tags used in the Playwright BDD features.

CLI example:

```bash
cd {PROJECT_ROOT}
./.venv/bin/python src/qe_agent/tagging/extract_tags.py
```

This returns the set of unique tags discovered from the feature files, in a stable, de-duplicated order.

### Slice 3: Tag Description Agent

Purpose: Attach a short plain-English description to each tag, using known descriptions when available and a generic fallback when unknown.

CLI example:

```bash
cd {PROJECT_ROOT}
printf '%s\n' '@alpha' '@beta' '@gamma' '@unknown-tag' > /tmp/qe_tags.txt
./.venv/bin/python src/qe_agent/tag_describer.py --tags-file /tmp/qe_tags.txt --descriptions-file /tmp/qe_tag_descriptions.json
```

This writes or updates a JSON registry of tag descriptions and prints a human-readable tag-to-description summary.

### Slice 4: Previous-Day Report + Tag Recommendation Agent

Purpose: Read the previous day’s report and generate an ordered list of tags to run next, with estimated durations.

CLI example:

```bash
cd {PROJECT_ROOT}
./.venv/bin/python src/qe_agent/tag_recommender.py \
  --report artifacts/ai-report.json \
  --descriptions src/qe_agent/tagging/tag_descriptions.json \
  --max-tags 3 \
  --output /tmp/tag_plan.json
```

This produces a short JSON plan such as:
- tag order
- tag priority
- estimated duration in seconds
- reasoning summary

### Slice 5: Run the Recommended Playwright Tags

Purpose: Take the tag plan and run the associated Playwright BDD tags in order.

CLI example:

```bash
cd {PROJECT_ROOT}
node scripts/orchestrate-tag-runner.js \
  --tag-plan /tmp/tag_plan.json \
  --project-dir ./banking-platform-voltio.QA/playwright
```

This executes the selected tags in sequence and exits with a compact JSON summary. The `--dry-run` flag is available for previewing the command flow without executing Playwright. In practice, the project is tag-agnostic: it consumes the ordered tags discovered from the feature suite and does not depend on a bank-specific tag list.

## Local Setup

Use the project-local virtual environment for Python commands:

```bash
cd {PROJECT_ROOT}
./.venv/bin/python -m pytest
```

To run the Playwright project from its own directory:

```bash
cd {PROJECT_ROOT}/banking-platform-voltio.QA/playwright
npm install
npx playwright test --grep @example-tag
```

## Validation Pattern

Each slice is intentionally kept small enough to be validated from the command line. The project follows a bounded workflow:

1. produce a compact summary
2. discover tags
3. describe tags
4. rank them from the prior-day report
5. run the top recommended tags

The goal is not a full autonomous system; it is a controlled, human-verifiable QA triage workflow.

## Future Copilot Integration (Deferred)

The current implementation remains CLI-first by design. The future VS Code Copilot entry point is intentionally isolated behind a thin adapter in `src/qe_agent/copilot_adapter.py`, which converts a chat prompt into repo-local CLI arguments without changing the core QA triage flow.

Example contract:

```python
from qe_agent.copilot_adapter import build_cli_args_from_prompt

args = build_cli_args_from_prompt(
    "Run the triage flow for artifacts/ai-report.json and banking-platform-voltio.QA/playwright/tests/bdd/features in dry run"
)
# -> {"report_path": "artifacts/ai-report.json", "feature_dir": "banking-platform-voltio.QA/playwright/tests/bdd/features", "dry_run": True, "max_tags": 10}
```

This keeps the IDE trigger bounded to a single short prompt, a single CLI invocation, and a compact output footprint. The adapter is not part of the active execution path; it is a future refactor point for the IDE integration slice.

## Notes

- The current scope is CLI-first and intentionally bounded.
- Copilot/IDE integration is deferred to a future slice.
- Generated files are kept out of commits via the repository `.gitignore`.
- The project is meant to be simple, reviewable, and easy to iterate on without broad architecture overhead.

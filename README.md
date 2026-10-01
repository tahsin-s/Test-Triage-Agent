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
cd /home/tahsins/git/Test-Triage-Agent
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
cd /home/tahsins/git/Test-Triage-Agent
./.venv/bin/python src/qe_agent/tagging/extract_tags.py
```

This returns the set of unique tags discovered from the feature files, in a stable, de-duplicated order.

### Slice 3: Tag Description Agent

Purpose: Attach a short plain-English description to each tag, using known descriptions when available and a generic fallback when unknown.

CLI example:

```bash
cd /home/tahsins/git/Test-Triage-Agent
printf '%s\n' '@CreatesData' '@SmokeTest' '@fail' '@UnknownTag' > /tmp/qe_tags.txt
./.venv/bin/python src/qe_agent/tag_describer.py --tags-file /tmp/qe_tags.txt --descriptions-file /tmp/qe_tag_descriptions.json
```

This writes or updates a JSON registry of tag descriptions and prints a human-readable tag-to-description summary.

### Slice 4: Previous-Day Report + Tag Recommendation Agent

Purpose: Read the previous day’s report and generate an ordered list of tags to run next, with estimated durations.

CLI example:

```bash
cd /home/tahsins/git/Test-Triage-Agent
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
cd /home/tahsins/git/Test-Triage-Agent
node scripts/orchestrate-tag-runner.js \
  --tag-plan /tmp/tag_plan.json \
  --project-dir ./banking-platform-voltio.QA/playwright
```

This executes the selected tags in sequence and exits with a compact JSON summary. The `--dry-run` flag is available for previewing the command flow without executing Playwright.

## Local Setup

Use the project-local virtual environment for Python commands:

```bash
cd /home/tahsins/git/Test-Triage-Agent
./.venv/bin/python -m pytest
```

To run the Playwright project from its own directory:

```bash
cd /home/tahsins/git/Test-Triage-Agent/banking-platform-voltio.QA/playwright
npm install
npx playwright test --grep @CreatesData
```

## Validation Pattern

Each slice is intentionally kept small enough to be validated from the command line. The project follows a bounded workflow:

1. produce a compact summary
2. discover tags
3. describe tags
4. rank them from the prior-day report
5. run the top recommended tags

The goal is not a full autonomous system; it is a controlled, human-verifiable QA triage workflow.

## Notes

- The current scope is CLI-first and intentionally bounded.
- Copilot/IDE integration is deferred to a future slice.
- Generated files are kept out of commits via the repository `.gitignore`.
- The project is meant to be simple, reviewable, and easy to iterate on without broad architecture overhead.

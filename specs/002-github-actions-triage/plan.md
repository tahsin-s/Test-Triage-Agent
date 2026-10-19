# Implementation Plan: GitHub Actions QA Triage

**Branch**: `002-github-actions-triage` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-github-actions-triage/spec.md`

**Note**: This plan is intentionally slice-based so each milestone is human-verifiable from the CLI or the GitHub UI.

## Summary

Build a bounded GitHub Actions triage loop in which a developer asks Copilot from the IDE to review a remote branch, retrieve the Playwright tag inventory and prior report, generate missing tag descriptions, order the next test run by risk, and dispatch the ordered tag plan to GitHub Actions. The workflow executes only the selected tags in the specified sequence and emits a compact summary for the next cycle.

## Technical Context

**Language/Version**: Python 3.11; JavaScript/Node.js for Playwright orchestration; GitHub Actions YAML

**Primary Dependencies**: Python standard library, pytest, `gh` CLI optional, GitHub Actions, Playwright, existing repo scripts under `src/qe_agent` and `scripts/`

**Storage**: Repository-local artifacts plus GitHub Actions workflow run metadata and artifacts

**Testing**: pytest for Python logic; Playwright suite for execution validation; dry-run commands for local verification

**Target Platform**: Linux workstations and GitHub-hosted runners

**Project Type**: CLI + GitHub automation integration for QA triage

**Performance Goals**: Keep each slice under a single bounded execution path; prioritize tag order and risk reduction over broad suites; produce a compact artifact summary

**Constraints**: Must stay within a maximum tag count per cycle; must not auto-loop; must fail clearly when artifacts or branch state are unavailable; must keep secrets out of logs and workflow payloads

**Scale/Scope**: Single repository, one feature area or branch at a time, bounded remote workflow execution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: The solution remains lightweight and reviewable rather than broad or heavyweight.
- PASS: The implementation preserves the repo’s Python venv-based execution model.
- PASS: The design keeps a clear boundary between Copilot planning and GitHub Actions execution.
- PASS: Sensitive data handling is protected through compact payloads and no secrets in workflow logs or payloads.

## Project Structure

### Documentation (this feature)

```text
specs/002-github-actions-triage/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── copilot-to-github-actions.md
├── spec.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
.github/
├── agents/
│   ├── qa-triage.agent.md
│   ├── tag-prioritizer.agent.md
│   └── tag-runner.agent.md
├── copilot-instructions.md
└── workflows/
    └── triage-playwright.yml  # to be added in implementation

scripts/
├── orchestrate-tag-runner.js
├── prepare-ai-test-output.js
├── tag-describer.js
└── list-bdd-tags.js

src/
├── qe_agent/
│   ├── tag_describer.py
│   ├── tag_recommender.py
│   ├── copilot_adapter.py
│   ├── reporting/
│   ├── tagging/
│   ├── recommendation/
│   └── orchestration/
├── qe_agent_cli.py
└── __init__.py

banking-platform-voltio.QA/playwright/
├── tests/
├── src/
├── generated/
├── playwright.config.ts
└── package.json
```

**Structure Decision**: Keep the GitHub Actions integration thin and repo-native. The repository already contains the deterministic parsing logic and tag execution commands; the new implementation adds the workflow contract, remote dispatch layer, and review checkpoints without re-architecting the existing code.

## Slice-Based Implementation Plan

### Slice 1: Contract and GitHub Setup

Goal: establish the contract and one-time GitHub prerequisites.

Work:
- define the Copilot-to-GitHub payload schema
- confirm `Actions` is enabled
- confirm workflow permissions and repository secrets are in place
- verify the repo branch is valid for workflow runs

Human-verifiable result:
- GitHub repo shows Actions enabled and workflow can be triggered manually from the UI.
- Local CLI can still run the existing tag/report scripts, proving the repo state is valid.

### Slice 2: Remote Branch Artifact Retrieval

Goal: make the remote branch provide the tag list and prior report to Copilot.

Work:
- add a workflow or script that reads the branch artifact source and prior report
- validate that the parser consumes report data deterministically
- expose the branch metadata in a compact summary

Human-verifiable result:
- `gh workflow run` or Actions UI shows a workflow run with a summary artifact.
- `python src/qe_agent/reporting/prepare_playwright_output.py` can generate the same compact summary locally.

### Slice 3: Tag Discovery and Description Resolution

Goal: make missing or unknown tags describe themselves.

Work:
- extend the tag discovery flow to compare against the known description registry
- add or update known descriptions for unknown tags using the scenario text
- persist the updated registry in a canonical location

Human-verifiable result:
- CLI output shows the tag registry before and after description resolution.
- GitHub job logs show the same tag list and descriptions for the branch under test.

### Slice 4: Ordered Tag Planning

Goal: turn the prior report and tag descriptions into a bounded execution order.

Work:
- read prior report failure signals
- rank tags by likely impact and runtime
- enforce the configured maximum tag cap
- emit a compact JSON plan

Human-verifiable result:
- A JSON file is generated locally with ordered tags and rationale.
- The workflow can inspect that same order before any test run begins.

### Slice 5: Workflow Dispatch and Playwright Execution

Goal: send the tag plan to GitHub Actions and execute the selected tests in order.

Work:
- add YAML workflow trigger(s) for branch and manual dispatch
- send the chosen tag list as workflow inputs
- run `npx playwright test --grep` or the repo’s orchestrator against only the selected tags
- upload the final report artifact

Human-verifiable result:
- GitHub Actions shows the exact list of tags selected for the run.
- Workflow logs show the tags were executed in the received order.

### Slice 6: Closed-Loop Validation

Goal: validate the end-to-end loop without broadening the suite.

Work:
- confirm the next run can be triggered after a prior run publishes its summary
- confirm the new report becomes the basis for the next tag ordering cycle
- validate the compact artifact summary is readable by both humans and Copilot

Human-verifiable result:
- A developer can review the new artifact and the next tag plan in either the Actions tab or the CLI output.

## Implementation Sequence

1. Confirm repo-level contract and GitHub setup
2. Add deterministic artifact retrieval and summary generation
3. Add tag description enrichment and registry updates
4. Add the ordered tag planning step
5. Add the remote GitHub Actions workflow dispatch
6. Run the full bounded cycle and confirm artifact publication

## Complexity Tracking

No constitution violations require a justification for this feature. The design intentionally avoids broad architecture and keeps the implementation aligned with the repo’s lightweight delivery model.

# Implementation Plan: Agentic QE Reporting

**Branch**: `001-agentic-qe-reporting` | **Date**: 2026-09-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-agentic-qe-reporting/spec.md`

**Note**: This is the minimal viable implementation plan for a POC centered on a shell-driven, disposable validation workflow.

## Summary

Build a lightweight daily quality-check workflow that runs inside a disposable Linux environment, selects the relevant app or feature validation path, executes the associated test commands, and produces a short, leadership-friendly summary. The implementation intentionally stays small: a shell entry point, a Python helper for secure execution and reporting, and a compact test suite to validate redaction and reporting logic.

This MVP remains CLI-first and human-callable. The VS Code Copilot Chat entry point is intentionally deferred to a later integration slice so the core workflow can be validated without coupling the first implementation to a specific IDE integration contract.

This plan is intentionally bounded. The goal is to finish a useful MVP in a limited time with explicit hard stops, not to produce a never-ending autonomous workflow. Every slice must stop at a predefined boundary, include a clear exit status, and emit only a compact artifact that a human can review quickly.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, shell utilities (`bash`, `find`, `grep`, `mktemp`)

**Storage**: Temporary workspace or disposable VM folder; no long-lived shared artifacts beyond the active run

**Testing**: pytest for unit/integration checks; shell script for orchestration execution

**Target Platform**: Linux workstation or disposable VM used from VS Code

**Project Type**: CLI automation / QA workflow tool

**Integration Model**: The active MVP is a repo-local CLI workflow that runs from the project venv and returns a small artifact for human review. VS Code Copilot Chat integration is intentionally postponed to a future slice and is not part of the current implementation scope.

**Performance Goals**: Validate a feature or app area in under 10 minutes; generate the daily summary within 1 minute of test completion; keep each slice bounded to a single short execution path

**Constraints**: Must avoid exposing `.env` values, PII, or credentials; code and tests must run in a venv; artifacts must be removed within 24 hours

**Scale/Scope**: Single repository, daily release checks, one app or feature area at a time

**Hard-Stop Guardrails**:
- Each slice has a maximum runtime of 30 minutes end-to-end from invocation to completion.
- Each CLI command must produce a single summary artifact and must not exceed 300 lines of human-readable output unless a user explicitly asks for more detail.
- The orchestrator may recommend at most 10 tags per run and must stop if more than 10 are required.
- The system must stop after one pass, one retry, and one fallback path; no infinite re-queues or endless loops.
- Report generation must be capped to a single daily snapshot and a single AI-friendly summary file per run.
- Any failure or timeout must surface a compact error summary and exit with a non-zero status rather than continuing silently.
- Copilot Chat integration remains deferred and should not add runtime or output complexity to the active MVP slice set.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: The project stays intentionally lightweight to maximize development velocity.
- PASS: The implementation avoids rigid platform complexity and favors a shell-based POC approach.
- PASS: Python execution is required inside a project-local virtual environment.
- PASS: Sensitive data handling is prioritized by default, in line with the security constraints in the idea document.

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-qe-reporting/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
├── spec.md
└── checklists/
```

### Source Code (repository root)

```text
scripts/
├── run_qe_check.sh
├── cleanup_qe_env.sh
└── .venv/

src/
├── qe_agent/
│   ├── __init__.py
│   ├── runner.py
│   ├── report.py
│   ├── tag_recommender.py
│   ├── recommendation/
│   ├── tagging/
│   └── sanitization.py
├── qe_agent_cli.py
└── __init__.py

tests/
├── unit/
│   └── test_report_builder.py
├── integration/
│   └── test_qe_runner.py
└── fixtures/
    └── sample_run_output.txt
```

**Structure Decision**: A single CLI-oriented structure is the simplest fit for this POC. The shell script handles environment creation and execution; Python modules handle test orchestration, sanitization, and summary generation; a later Copilot integration slice may wrap the same bounded workflow if the IDE entry point is needed in the future.

## Complexity Tracking

No constitution violations require a justification for this minimal POC.

---

## Phase 0: Research and Decisions

- Choose a disposable Linux workspace over a persistent VM-per-user model to minimize cost and setup overhead.
- Use Python within a local virtual environment for all automation logic, tests, and helper routines.
- Keep the active MVP focused on a CLI-first workflow that a human can run directly in the repo.
- Defer Copilot Chat integration to a dedicated future slice so current implementation remains small, testable, and reviewable.
- Have the shell entry script accept a repo path and a target scope so the workflow can run either a whole app or a specific feature area.
- Keep the output concise: top findings, pass/fail status, and a few important metrics.
- Treat redaction and cleanup as first-class requirements rather than optional afterthoughts.
- Add explicit hard-stop checkpoints before implementation: runtime cap, output cap, retry cap, and tag cap.

## Phase 1: Design Outputs

- Create a research summary documenting the shell + Python execution model and the reasons for the minimal POC design.
- Define the underlying entities for a test run, a finding, and a daily summary.
- Define a lightweight command interface that can be invoked from VS Code and return a compact JSON or text summary.
- Define a future Copilot integration slice separately so the active MVP does not lock in IDE-specific behavior prematurely.
- Produce a quickstart guide that proves the environment setup and execution flow in a venv.

## Phase 2: Recommended POC Scope

1. Create a shell script that:
   - creates a temporary execution directory
   - selects the target repo or feature area
   - runs the relevant validation commands
   - captures exit codes and extracted output

2. Create a Python helper layer that:
   - validates the target path and selected scope
   - strips secrets and PII before producing any report
   - aggregates pass/fail status into a short summary
   - removes temporary artifacts on completion or after the retention window

3. Add a minimal test suite that verifies:
   - report formatting logic
   - secret redaction rules
   - exit-code handling for failing validation commands

4. Keep all Python execution within a local `.venv` and document the exact commands for activation and setup in quickstart.md.

## Key Risks

- The target repo may not expose stable or easy-to-run tests.
- Some validation commands may depend on services or environment setup that are not yet automated.
- A daily report must avoid showing secrets from `.env` or other sensitive files.

These risks are acceptable for the initial POC and can be addressed in later iterations without adding broad architecture overhead.

## Definition of Done for the POC

- A user can run a single shell script to trigger a test validation in a disposable environment.
- A compact report is created summarizing the key outcomes.
- Secrets and environment artifacts are sanitized and removed according to the retention policy.
- The workflow runs from a Python venv and does not rely on global package installs.
- The scope remains intentionally narrow and suitable for a sales/demo conversation.
- Each slice stops automatically when it reaches its runtime cap, output cap, or retry budget.
- The user receives a short, actionable summary at exit instead of an endless stream of logs or a silent hang.
- No slice may continue after a failed validation without a clear reason and a bounded fallback path.

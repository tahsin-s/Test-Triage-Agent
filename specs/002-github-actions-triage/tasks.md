# Tasks: GitHub Actions QA Triage

**Input**: Design documents from `/specs/002-github-actions-triage/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the repo scaffolding and GitHub workflow boundary for the remote branch triage flow.

- [ ] T001 Create the feature scaffolding and implementation notes in `specs/002-github-actions-triage/plan.md`, `specs/002-github-actions-triage/research.md`, `specs/002-github-actions-triage/data-model.md`, and `specs/002-github-actions-triage/quickstart.md`
- [ ] T002 [P] Initialize the workflow contract and example payload in `.github/workflows/triage-playwright.yml` and `specs/002-github-actions-triage/contracts/copilot-to-github-actions.md`
- [ ] T003 [P] Confirm the repo’s Copilot agent surface aligns with the branch triage design in `.github/agents/qa-triage.agent.md`, `.github/agents/tag-prioritizer.agent.md`, and `.github/agents/tag-runner.agent.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared execution path that every user story relies on.

- [ ] T004 Define the bounded execution contract for branch, tag list, and max tag count in `src/qe_agent/copilot_adapter.py` and `specs/002-github-actions-triage/contracts/copilot-to-github-actions.md`
- [ ] T005 [P] Add a GitHub Actions workflow input validator in `.github/workflows/triage-playwright.yml` to reject empty or malformed tag payloads
- [ ] T006 [P] Add repo-local dry-run orchestration and validation hooks in `scripts/orchestrate-tag-runner.js` and `src/qe_agent/orchestration/run_selected_tests.py`
- [ ] T007 Add deterministic report-parsing contract checks in `src/qe_agent/reporting/prepare_playwright_output.py` and `artifacts/ai-report.json`
- [ ] T008 Add a stable tag registry read/write path for unknown tags in `src/qe_agent/tag_describer.py` and `src/qe_agent/tagging/`
- [ ] T009 Add a bounded tag-plan output contract in `src/qe_agent/tag_recommender.py` and `artifacts/tag_plan.json`

**Checkpoint**: The repo can validate local tag inventory and report data, and it has a bounded execution contract ready for remote dispatch.

---

## Phase 3: User Story 1 - Developer requests a branch-aware triage run from the IDE (Priority: P1) 🎯 MVP

**Goal**: Let a developer ask Copilot for a remote branch QA triage run without manually assembling the scripts and arguments.

**Independent Test**: A developer can run the local CLI or prompt Copilot with a branch-aware request and confirm the tool identifies the target branch, report path, and tag cap before any execution begins.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add a prompt parsing test for IDE request parsing in `tests/unit/test_copilot_adapter.py`
- [ ] T011 [P] [US1] Add a CLI smoke test for the bounded adapter flow in `tests/integration/test_copilot_adapter.py`

### Implementation for User Story 1

- [ ] T012 [P] [US1] Expand `src/qe_agent/copilot_adapter.py` to parse branch, feature, report, and max-tag request details from the IDE prompt
- [ ] T013 [US1] Update `.github/agents/qa-triage.agent.md` to include the remote branch fetch, report retrieval, and ranking stages in the user-visible flow
- [ ] T014 [US1] Update `.github/copilot-instructions.md` to reference the branch-aware triage flow and the new workflow contract
- [ ] T015 [US1] Validate the prompt-to-CLI translation by running `python src/qe_agent/copilot_adapter.py "Run the branch triage flow for main with max tags 3"` in the repo root

**Checkpoint**: User Story 1 is independently testable and produces a valid, bounded request payload without manual command assembly.

---

## Phase 4: User Story 2 - Copilot resolves unknown tags and orders execution by risk (Priority: P2)

**Goal**: Ensure the triage flow can handle newly introduced tags and prioritize them with a bounded, risk-based execution order.

**Independent Test**: Given a known report and an unknown tag, the flow can generate a description, place the tag in the ordered plan, and keep the total under the configured tag cap.

### Tests for User Story 2

- [ ] T016 [P] [US2] Add a unit test for unknown-tag description generation in `tests/unit/test_tag_descriptions.py`
- [ ] T017 [P] [US2] Add a unit test that verifies tag ordering remains bounded by `max_tags` in `tests/unit/test_tag_recommender.py`

### Implementation for User Story 2

- [ ] T018 [P] [US2] Update `src/qe_agent/tag_describer.py` to compare discovered tags with the known registry and generate missing descriptions from BDD feature text
- [ ] T019 [US2] Update `src/qe_agent/tag_recommender.py` to combine risk signals from the prior report and tag descriptions into a ranked, bounded plan
- [ ] T020 [US2] Update `.github/agents/tag-prioritizer.agent.md` to describe the selection order and risk-based recommendation flow
- [ ] T021 [US2] Validate the ordered tag flow with `./.venv/bin/python src/qe_agent/tag_recommender.py --report artifacts/ai-report.json --descriptions src/qe_agent/tagging/tag_descriptions.json --max-tags 3 --output /tmp/tag_plan.json`

**Checkpoint**: User Story 2 produces an ordered, bounded tag plan that is stable, explainable, and ready for GitHub Actions dispatch.

---

## Phase 5: User Story 3 - GitHub Actions executes the selected tag plan in order (Priority: P3)

**Goal**: Dispatch the final plan to GitHub Actions and run only the selected Playwright tags in the received order.

**Independent Test**: A valid workflow dispatch with an ordered tag list triggers the GitHub Actions run, executes only those tags in the correct order, and publishes a summary artifact.

### Tests for User Story 3

- [ ] T022 [P] [US3] Add a workflow validation test for ordered tag execution in `tests/integration/test_qe_runner.py`
- [ ] T023 [P] [US3] Add a local dry-run contract test for `scripts/orchestrate-tag-runner.js` in `tests/unit/test_orchestrator.py`

### Implementation for User Story 3

- [ ] T024 [US3] Build the GitHub Actions workflow in `.github/workflows/triage-playwright.yml` to accept `branch`, `tags`, and `max_tags` inputs, validate them, and run only the selected test set
- [ ] T025 [P] [US3] Update `scripts/orchestrate-tag-runner.js` to invoke the repo’s orchestrator with the exact ordered tags and a bounded `--dry-run` option
- [ ] T026 [P] [US3] Update `src/qe_agent/orchestration/run_selected_tests.py` to resolve the selected tags from the plan and run the Playwright suite in list order
- [ ] T027 [US3] Add artifact publishing and summary reporting in `.github/workflows/triage-playwright.yml` so the result is visible in GitHub Actions and can feed the next triage cycle
- [ ] T028 [US3] Validate the remote contract with a dry run: `node scripts/orchestrate-tag-runner.js --tag-plan /tmp/tag_plan.json --project-dir ./banking-platform-voltio.QA/playwright --dry-run`
- [ ] T029 [US3] Validate the web-side GitHub setup by enabling Actions and confirming the repository settings page is ready for workflow dispatch in the GitHub web UI

**Checkpoint**: A valid workflow dispatch can execute the selected Playwright tags in the specified order and publish a compact summary artifact.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, clarity, and validation across all stories.

- [ ] T030 [P] Add or update user-facing guidance in `specs/002-github-actions-triage/quickstart.md` for CLI validation and GitHub UI validation
- [ ] T031 [P] Review and tighten the GitHub Action workflow logs and artifact output in `.github/workflows/triage-playwright.yml`
- [ ] T032 [P] Run the local validation suite: `./.venv/bin/python -m pytest` from the repository root
- [ ] T033 Run the branch triage smoke test end-to-end: `./.venv/bin/python src/qe_agent/tag_recommender.py --report artifacts/ai-report.json --descriptions src/qe_agent/tagging/tag_descriptions.json --max-tags 3 --output /tmp/tag_plan.json` and `node scripts/orchestrate-tag-runner.js --tag-plan /tmp/tag_plan.json --project-dir ./banking-platform-voltio.QA/playwright --dry-run`
- [ ] T034 Final review of repo status and readiness for GitHub workflow trigger in the remote GitHub UI

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies
- Foundational (Phase 2): depends on Setup
- User Story 1 (Phase 3): depends on Foundational
- User Story 2 (Phase 4): depends on Foundational and User Story 1 for scope validation, but should remain independently testable
- User Story 3 (Phase 5): depends on Foundational and the prior two stories
- Polish (Phase 6): depends on all story milestones and validation checks

### Parallel Opportunities

- T002 and T003 can run in parallel during Phase 1
- T005, T006, T008, and T009 can run in parallel within Phase 2 once the contract is agreed
- T010 and T011 can run in parallel for User Story 1
- T016 and T017 can run in parallel for User Story 2
- T022 and T023 can run in parallel for User Story 3
- T030, T031, and T032 can run in parallel during the final polish phase

### Implementation Strategy

1. Complete Phase 1 and Phase 2 to establish the bounded contract and execution model.
2. Deliver User Story 1 as the MVP: prompt-to-request translation and bounded branch request.
3. Add User Story 2: unknown tags and ordered risk-based selection.
4. Add User Story 3: remote execution and artifact reporting.
5. Finish with final validation and documentation cleanup.

### User Story Completion Criteria

- User Story 1 complete when Copilot can convert an IDE request into a valid branch-aware triage payload.
- User Story 2 complete when a tag plan can be generated from prior report + descriptions while respecting the tag cap.
- User Story 3 complete when GitHub Actions can run only the selected tags in the given order and publish an artifact summary.

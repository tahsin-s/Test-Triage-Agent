# Tasks: Agentic QE Reporting

**Input**: Design documents from `/specs/001-agentic-qe-reporting/`

**Purpose**: Split the feature into clear, human-verifiable slices so the working CLI-first QA triage workflow stays small, bounded, and easy to review before any VS Code Copilot integration is introduced.

**Out of Scope**: This slice plan intentionally excludes full cloud orchestration, persistent scheduling, broad auto-healing, long-lived memory systems, and Copilot-specific chat integration. Those belong to a later platform phase.

## Phase 1: Slice Boundary and Out-of-Scope Definition

**Purpose**: Define the product boundary and the MVP constraints so the workflow stays easy to review and operate.

- [ ] T001 Define the product boundary and explicitly list the out-of-scope items for the first-pass agentic QE workflow in specs/001-agentic-qe-reporting/spec.md
- [ ] T002 [P] Define the CLI-first operating model and the human verification pattern in specs/001-agentic-qe-reporting/plan.md
- [ ] T003 [P] Record the default user flow for CLI verification in specs/001-agentic-qe-reporting/quickstart.md

## Hard-Stop Rules for All Slices

Each slice must follow these explicit guardrails so implementation remains finite and reviewable:

- [ ] H001 Set a maximum runtime of 10 minutes for any single slice invocation.
- [ ] H002 Cap all generated output to a single summary artifact and a maximum of 300 lines of human-readable content.
- [ ] H003 Enforce a maximum of 10 recommended tags in any orchestration plan; if more are needed, stop and ask for a narrower scope.
- [ ] H004 Limit each script to one execution pass, one retry, and one fallback path before exiting with a clear failure summary.
- [ ] H005 Fail fast on missing inputs, invalid paths, or malformed reports; do not loop forever or continue silently.
- [ ] H006 Ensure all scripts emit a final short status line with exit code and artifact path before terminating.
- [ ] H007 Keep each slice bounded to a single execution pass, with a compact result and no long-running unattended process.

---

## Phase 2: Slice 1 - Prepare Playwright Output for an AI

**Goal**: Give a human a script that converts raw Playwright output into a compact AI-ready summary.

**Human CLI**: `node scripts/prepare-ai-test-output.js --report-dir ./playwright-report --output ./artifacts/ai-report.json`

- [X] T004 Create the script entry in scripts/prepare-ai-test-output.js to read the generated HTML or JSON report and summarize test status
- [X] T005 [P] Parse the Playwright report to extract suite name, pass/fail counts, failed tests, and failure summary in src/qe_agent/reporting/prepare_playwright_output.py
- [X] T006 [P] Normalize the output into a compact JSON payload suitable for AI prompts in src/qe_agent/reporting/normalize_report.py
- [X] T007 Add a CLI contract with argument validation and a dry-run mode in scripts/prepare-ai-test-output.js
- [X] T008 Add a focused test in tests/unit/test_prepare_ai_output.py that verifies failure summaries are sanitized and concise

**Validation**: Run the script against the existing report and confirm it produces a small, readable JSON summary without raw HTML noise. If the input report is too large or malformed, stop after one concise error message and exit non-zero.

---

## Phase 3: Slice 2 - Output All Available BDD Tags

**Goal**: Create a script that lists every tag in the automation suite in a stable, reviewable format.

**Human CLI**: `node scripts/list-bdd-tags.js --features ./banking-platform-voltio.QA/playwright/tests/bdd/features`

- [X] T009 Create the tag-discovery script in scripts/list-bdd-tags.js
- [X] T010 [P] Parse all Gherkin feature files and collect unique tags in src/qe_agent/tagging/extract_tags.py
- [X] T011 [P] Deduplicate, sort, and print tags in a stable output format in src/qe_agent/tagging/format_tags.py
- [X] T012 Add a test in tests/unit/test_tag_extraction.py that verifies tags are discovered and de-duped correctly
- [X] T013 Add a CLI option to output JSON or plain text so humans can inspect the list without parsing code

**Validation**: Run the script and confirm every discovered tag from the BDD suite is printed in a clear list. Do not stream a giant unbounded list; emit a sorted, capped list only.

---

## Phase 4: Slice 3 - Tag Description Agent (One-Shot, Minimal Reasoning)

**Goal**: Create a lightweight agent that describes the functionality of each tag in a single output pass.

**Human CLI**: `python src/qe_agent/tag_describer.py --tags-file ./artifacts/tags.json --output ./artifacts/tag-descriptions.md`

- [X] T014 Create the tag description agent entry in src/qe_agent/tag_describer.py
- [X] T015 [P] Read the tag list and return a one-shot description per tag in src/qe_agent/tagging/describe_tags.py
- [X] T016 [P] Ensure the output is minimal and human-readable, with one concise description per tag in src/qe_agent/tagging/render_descriptions.py
- [X] T017 Add a test in tests/unit/test_tag_descriptions.py that verifies the output contains a tag name and a plain-English description
- [X] T018 Add a fallback rule for unknown or unlabeled tags so the agent returns a generic description instead of failing

**Validation**: Run the agent on the discovered tag list and verify the output is short, clear, and understandable by a human reviewer. Stop after the first completed pass and do not continue generating broader explanations once the list is described.

---

## Phase 5: Slice 4 - Previous-Day Report + Tag Recommendation Agent

**Goal**: Read yesterday’s report and the tag descriptions, then recommend which tags to run, in what order, and how long they should take.

**Human CLI**: `python src/qe_agent/tag_recommender.py --report ./artifacts/yesterday-report.json --descriptions ./artifacts/tag-descriptions.md --output ./artifacts/tag-plan.json`

- [X] T019 Create the recommendation agent entry in src/qe_agent/tag_recommender.py
- [X] T020 [P] Parse yesterday’s report and identify the highest-risk failing or flaky areas in src/qe_agent/recommendation/read_report.py
- [X] T021 [P] Rank the tags by priority, estimated impact, and likely runtime in src/qe_agent/recommendation/score_tags.py
- [X] T022 [P] Return a clear execution order and a time estimate for each tag in src/qe_agent/recommendation/plan_run.py
- [X] T023 Add a test in tests/unit/test_tag_recommender.py that verifies the output includes tags, order, and duration estimates

**Validation**: Run the recommender against a sample previous-day report and confirm the output is a short ordered plan rather than a long explanation. If the plan exceeds the 10-tag limit, stop and return the top 10 by priority.

---

## Phase 6: Slice 5 - Orchestrator for Tag Selection and Test Execution

**Goal**: Only run the tag description agent when needed, call the recommender to get the tag plan, and then execute the selected Playwright tests.

**Human CLI**: `node scripts/orchestrate-tag-runner.js --report-dir ./playwright-report --feature-dir ./banking-platform-voltio.QA/playwright/tests/bdd/features --tag-plan ./artifacts/tag-plan.json`

- [X] T024 Create the orchestrator entry in scripts/orchestrate-tag-runner.js
- [X] T025 [P] Detect whether tag descriptions are already available and skip the description agent when they are current in src/qe_agent/orchestration/should_refresh_tags.py
- [X] T026 [P] Trigger the tag description agent only when required, then invoke the recommendation agent in src/qe_agent/orchestration/run_orchestration.py
- [X] T027 [P] Execute the selected Playwright BDD tags in the recommended order using the existing `npx playwright test --grep` flow in src/qe_agent/orchestration/run_selected_tests.py
- [X] T028 Add a CLI-safe summary output that includes the selected tag list, overall duration estimate, and run status in src/qe_agent/orchestration/summarize_run.py
- [X] T029 Add a test in tests/integration/test_orchestrator.py that verifies the orchestration flow produces the expected tag sequence and execution command

**Validation**: Run the orchestrator on a sample artifact set and verify it executes exactly the recommended tags in order. If the run exceeds the defined execution cap, abort after the current batch, emit a summary, and exit cleanly.

---

## Phase 7: Future Copilot Integration Slice (Deferred)

**Purpose**: Isolate the later VS Code Copilot Chat integration work so the current CLI-first implementation remains small and reviewable.

- [X] T030 Design the VS Code Copilot trigger contract and identify how the chat session will invoke the existing CLI workflow
- [X] T031 [P] Add a thin adapter layer that translates a Copilot chat prompt into the existing repo-local CLI arguments
- [X] T032 [P] Validate that the Copilot-triggered path remains bounded to a single chat turn and short output
- [X] T033 Document the future integration as a post-MVP refactor rather than part of the current slice implementation

---

## Phase 8: Final Verification and Demo Readiness

**Purpose**: Ensure each slice is independently callable and understandable by a human reviewer.

- [X] T034 [P] Run the slice scripts in order against a known sample report and confirm each one produces output without a broad or hidden setup step
- [X] T035 [P] Verify each script documents the command needed to run it from the CLI
- [X] T036 [P] Add a short README section that explains the five-slice workflow and how a human can verify behavior at each stage
- [X] T037 Confirm all generated artifacts are stored under a clear folder such as artifacts/ and remain easy to inspect

---

## Out of Scope (Explicitly Deferred)

These items are intentionally not included in the first five slices and should remain outside the MVP:

- [ ] O001 Full autonomous issue triage across multiple repos or distributed systems
- [ ] O002 Cloud scheduling, queue workers, or always-on background jobs
- [ ] O003 Persistent long-term memory or historical learning beyond the previous day report
- [ ] O004 Broad test auto-healing for flaky or random failures
- [ ] O005 Full dashboard or portal experience for non-CLI users
- [ ] O006 Multi-tenant orchestration or cross-team reporting at scale

## Dependencies & Execution Order

- **Phase 1** must finish before any slice scripts are implemented.
- **Slice 1** is the smallest, most reviewable starting point and should complete before Slice 2.
- **Slice 2** provides the input needed by Slice 3.
- **Slice 3** feeds the recommendation logic used in Slice 4.
- **Slice 4** provides the run plan consumed by Slice 5.
- **Final verification** runs after all slices complete.

## Parallel Opportunities

- T005, T006, and T007 can run in parallel within Slice 1.
- T010, T011, and T013 can run in parallel within Slice 2.
- T015, T016, and T018 can run in parallel within Slice 3.
- T020, T021, and T022 can run in parallel within Slice 4.
- T025, T026, and T027 can run in parallel within Slice 5.

## Implementation Strategy

### MVP First

1. Build Slice 1 and confirm the AI-ready report output is useful.
2. Build Slice 2 and validate the discovered tags are complete and human readable.
3. Build Slice 3 and verify the tag descriptions are short and accurate.
4. Build Slice 4 and confirm the ordering and time estimate logic is sensible.
5. Build Slice 5 and execute the selected tests in order.

### Human Verification Pattern

Each slice must remain callable from the command line and produce a small artifact that a person can inspect quickly before moving to the next step. The goal is not a hidden autonomous system; the goal is a layered workflow a human can validate at each boundary.

### Hard-Stop Execution Pattern

1. Validate inputs and scope immediately.
2. Run the step once with a bounded timeout.
3. If it exceeds runtime or output limits, stop and emit a concise summary.
4. Only then proceed to the next slice or ask for a narrower scope.
5. Exit with an explicit status line and artifact path so the user knows exactly what completed and what stopped.

# Feature Specification: GitHub Actions QA Triage

**Feature Branch**: `002-github-actions-triage`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "I need to prepare this to work forwith github actions. As a developer, I want to talk to an agent that will schedule and run tests for me on a remote github branch. Developer workspace: application code + .github agents. Remote git branch: Contains playwright test suite, and deterministic tag and playwright report parsing scripts. The interfaces I want to see are: Developer talks to Copilot from IDE. Copilot interfaces with github actions to retrieve tags and prior test report. Copilot generates descriptions for any unknown tags. Copilot orders tests based on prior report and tags. Copilot interfaces with github actions to send the list of which tags to run in what order. Github actions runs test-suite to specification."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer requests a remote branch triage run from the IDE (Priority: P1)

A developer working in the application codebase and the repository's GitHub agents wants to ask Copilot to schedule and run a focused set of Playwright tests for a remote GitHub branch without manually assembling the command flow. The developer expects the agent to operate on the branch state, fetch the relevant tag inventory and prior report, and return a safe, prioritized test plan before execution.

**Why this priority**: This is the main end-to-end user value. The developer needs a fast way to ask for a branch-aware triage run without leaving the IDE or manually combining scripts and GitHub artifacts.

**Independent Test**: Can be fully tested by asking Copilot to triage a known branch and confirming it retrieves the tag list and last report, then produces a bounded execution plan.

**Acceptance Scenarios**:

1. **Given** the developer is working on a branch that includes the Playwright suite and deterministic parsing scripts, **When** they ask Copilot to prepare a remote branch QA run, **Then** Copilot identifies the target branch, retrieves the available tags and the previous report, and summarizes the current risk picture.
2. **Given** the branch has a prior report and tag catalog, **When** the developer requests a triage plan, **Then** Copilot returns a compact, ordered list of tags and their rationale for the next run.

---

### User Story 2 - Copilot resolves missing tag descriptions and prioritizes execution (Priority: P2)

The agent should not depend on a complete tag registry for every run. For any unknown or newly introduced tags, Copilot should inspect the relevant feature scenarios, assign a concise description, and use that description together with the prior report to rank the tags by likely impact and urgency.

**Why this priority**: This prevents triage from stalling when the test suite evolves and ensures that ordering remains meaningful even as tags are introduced or renamed.

**Independent Test**: Can be fully tested by using a known branch with at least one unknown tag, running the description step, and confirming the tag is described and included in the ranked plan.

**Acceptance Scenarios**:

1. **Given** the tag registry does not contain a newly observed tag, **When** Copilot reviews the associated BDD scenarios, **Then** it creates a concise, human-readable description and stores it for future reuse.
2. **Given** the previous report shows failing or flaky areas, **When** Copilot ranks the discovered tags, **Then** it prioritizes the most relevant tags first while keeping the total within the defined execution cap.

---

### User Story 3 - GitHub Actions performs the selected test run in the requested order (Priority: P3)

Once Copilot has chosen the next tag order, it must send that execution plan to GitHub Actions, which then runs the Playwright suite in the specified sequence and records the result in a deterministic manner suitable for follow-up analysis.

**Why this priority**: This closes the loop from planning to execution and gives developers a reviewable, repeatable mechanism for running only the highest-value checks first.

**Independent Test**: Can be fully tested by submitting a known tag plan to the workflow, then confirming the workflow runs only the planned tags in order and produces a final result summary.

**Acceptance Scenarios**:

1. **Given** Copilot has produced a valid ordered tag plan, **When** it sends the run request to GitHub Actions, **Then** the workflow receives the exact tag sequence and executes the selected tests in that order.
2. **Given** a workflow run completes, **When** the results are published, **Then** the developer can review the pass/fail outcome and the next triage cycle can start from the new report.

---

### Edge Cases

- What happens when the remote branch has no previous report or the report is incomplete?
- How does the system handle a tag that exists in the feature suite but has no matching description?
- What happens when a workflow request includes tags beyond the allowed execution cap?
- How does the system behave when the GitHub Actions workflow fails before the selected tests start?
- What happens if the agent cannot access the remote branch artifacts or the branch is unavailable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a developer to request a branch-aware QA triage workflow from the IDE without manually composing the remote-branch execution steps.
- **FR-002**: Copilot MUST be able to retrieve the remote branch's Playwright tag inventory and the most recent prior test report from the GitHub Actions workflow or associated artifact store.
- **FR-003**: Copilot MUST compare discovered tags against the known tag description registry and identify any missing or unknown descriptions.
- **FR-004**: Copilot MUST generate a concise, plain-English description for any unknown tag using the relevant BDD scenario context.
- **FR-005**: Copilot MUST order the candidate tags using the prior report, tag descriptions, and risk or failure signals, while keeping the execution bounded to a safe maximum.
- **FR-006**: Copilot MUST send the selected tag list and execution order to GitHub Actions in a structured, reviewable format.
- **FR-007**: GitHub Actions MUST run the Playwright suite for the requested tags in the exact order specified by the agent.
- **FR-008**: The workflow MUST avoid broad or unbounded runs by limiting execution to the selected tags and a defined maximum count per cycle.
- **FR-009**: The system MUST emit a compact outcome summary after each run so the developer can review status without reading a large log stream.
- **FR-010**: The system MUST support repeated triage cycles: each run can update the tag descriptions and priority order based on the latest report and branch state.
- **FR-011**: The system MUST fail clearly when a remote artifact, branch, or workflow input is unavailable instead of silently proceeding with a stale or incomplete plan.

### Key Entities *(include if feature involves data)*

- **Developer**: The user who initiates a test triage request from their IDE and reviews the resulting action plan.
- **Remote Branch**: The GitHub branch that contains the Playwright suite, feature files, and any branch-specific test artifacts or source changes.
- **Tag Registry**: The collection of known tag names and their human-readable descriptions used to label and explain test areas.
- **Playwright Report**: The historical test report that captures pass/fail trends, failure clusters, and operational signals for prioritization.
- **Tag Plan**: The ordered list of selected tags and runtime or risk rationale produced by Copilot before execution.
- **GitHub Actions Workflow**: The automation layer that receives the selected plan and executes the specified Playwright test subset on the branch.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can request a branch-specific QA triage run from the IDE and receive a valid tag plan without manual script assembly in under 5 minutes.
- **SC-002**: Unknown tags are described and registered in the same triage cycle with at least 90% coverage for newly introduced tags encountered during the run.
- **SC-003**: The execution plan prioritizes the highest-risk tags first, reducing the time to detect the most relevant failures during a bounded test pass.
- **SC-004**: GitHub Actions runs only the selected tags in the specified order for each cycle and keeps the run within the defined execution cap.
- **SC-005**: Each run produces a concise summary that allows the developer to determine the next action without reviewing the full raw log output.
- **SC-006**: The workflow supports repeatable triage across multiple branch states without requiring manual intervention beyond the original developer request.

## Assumptions

- The remote branch already contains a valid Playwright test suite and deterministic parsing scripts for tags and reports.
- The repository provides a stable artifact or workflow endpoint for the prior test report and tag results.
- GitHub Actions can receive structured inputs and run the Playwright suite for a specific branch without requiring broader product changes.
- The IDE user is working in a repository that includes the shared GitHub agent definitions and supporting scripts for the triage workflow.
- If a prior report is missing, the system falls back to a safe default ordering based on tag metadata and the current branch state rather than triggering a broad full-suite run.

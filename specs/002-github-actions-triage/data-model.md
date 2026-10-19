# Data Model: GitHub Actions QA Triage

## Core entities

### DeveloperRequest

Represents the human ask that starts the branch triage flow.

Fields:
- `request_id`: unique request identifier
- `developer`: user or agent identity that initiated the request
- `branch`: target remote GitHub branch
- `target_scope`: application area or Playwright suite scope
- `max_tags`: hard cap for the ordered execution plan
- `requested_at`: timestamp when the request was issued

Validation rules:
- `branch` must be a non-empty branch name.
- `max_tags` must be greater than zero and capped to the workflow’s configured limit.
- `target_scope` must be one of the supported scopes for the repo.

Relationships:
- A `DeveloperRequest` creates one `TagPlan` and one `WorkflowDispatch`.

### RemoteBranchContext

Represents the branch state and its test assets.

Fields:
- `branch_name`
- `repo_name`
- `default_branch`
- `has_playwright_suite`
- `report_artifact_uri`
- `tag_registry_path`
- `last_known_commit`

Validation rules:
- `repo_name` and `branch_name` must be present when the workflow is invoked.
- `has_playwright_suite` must be true for the remote run to proceed.
- `report_artifact_uri` can be null only if the workflow handles a cold start without prior report.

Relationships:
- `RemoteBranchContext` provides context to `PriorReport` and `TagCatalog`.

### TagCatalog

Contains the list of tags discovered in the target branch.

Fields:
- `tags`: list of `TagEntry`
- `generated_at`
- `source`: branch commit or artifact source

Validation rules:
- Each tag must be unique.
- Tags should be persisted as stable strings beginning with `@` when applicable.

Relationships:
- `TagCatalog` is evaluated against `TagRegistry` and `TagDescription` entries.

### TagEntry

Represents one discovered Playwright tag.

Fields:
- `name`: tag name, e.g. `@smoke`
- `feature_file`: path to the feature file that contributed the tag
- `description`: optional plain-English explanation
- `is_known`: boolean derived from the description registry

Validation rules:
- `name` must be present.
- `description` may be null until description resolution occurs.

### PriorReport

Stores the most recent branch report and the associated failure signals.

Fields:
- `report_path`
- `summary`: pass/fail counts and duration
- `top_failures`: list of failure categories or feature areas
- `generated_at`

Validation rules:
- Summary must include enough data to rank tags without requiring the raw HTML report.
- `top_failures` must be a stable list of identifiers used for recommendation.

Relationships:
- Used to create `TagPlan` recommendations.

### TagPlan

The generated ordered set of tags selected for execution.

Fields:
- `plan_id`
- `requested_branch`
- `tags`: ordered list of `SelectedTag`
- `max_tags`
- `generated_by`: `copilot` or equivalent orchestration layer
- `generated_at`

Validation rules:
- `tags` length must be between 1 and `max_tags`.
- Order in the list must represent the exact execution sequence.

Relationships:
- `TagPlan` is sent to `WorkflowDispatch`.

### SelectedTag

A tag in the plan after prioritization.

Fields:
- `tag_name`
- `description`
- `priority_score`
- `estimated_duration_seconds`
- `reasoning`

Validation rules:
- `tag_name` must be present.
- `priority_score` must be numeric.
- `estimated_duration_seconds` should be non-negative.

### WorkflowDispatch

The remote request payload sent to GitHub Actions.

Fields:
- `workflow_name`
- `ref`
- `inputs`
- `status`
- `run_id`

Validation rules:
- `ref` must reference the target branch or commit.
- `inputs` must contain a valid ordered `tags` list.
- `status` must reflect the dispatch lifecycle: queued, running, succeeded, failed.

Relationships:
- A `WorkflowDispatch` executes the branch-specific `PlaywrightRun`.

### PlaywrightRun

The actual test run executed by GitHub Actions.

Fields:
- `run_id`
- `artifact_path`
- `status`
- `duration_seconds`
- `selected_tags`
- `summary`

Validation rules:
- `selected_tags` must match the request order exactly.
- `status` must be final after completion or fail-fast when a runner error occurs.

## State transitions

- `DeveloperRequest` -> `TagPlan` -> `WorkflowDispatch` -> `PlaywrightRun` -> `PriorReport` update
- `TagCatalog` may be updated during description resolution and then fed back into the next `TagPlan`.

## Notes on bounded execution

The system intentionally enforces a single-pass workflow that stops after one ordered tag plan is generated and dispatched. It does not continue re-queuing or broadening the suite unless the user explicitly asks for a new cycle.

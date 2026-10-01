<!--
Sync Impact Report
- Version change: 0.0.0 -> 1.0.0
- Modified principles: new constitution for Test Triage Agent
- Added sections: Core Principles, Additional Constraints, Development Workflow, Governance
- Removed sections: template placeholder sections and strict compliance gates
- Templates requiring updates: .specify/templates/plan-template.md ✅ reviewed; .specify/templates/spec-template.md ✅ reviewed; .specify/templates/tasks-template.md ✅ reviewed
- Follow-up TODOs: none
-->

# Test Triage Agent Constitution

## Core Principles

### I. Velocity Over Bureaucracy
The project prioritizes moving quickly and learning by shipping. Work should be organized around the smallest useful iteration, with the lightest process that still keeps the team aligned. We do not add review steps, ceremony, or documentation overhead unless they clearly reduce real risk or confusion.

### II. Freedom to Choose the Simple Working Solution
Teams are free to choose the tools, patterns, and structures that solve the problem with the least friction. There is no requirement to force every feature through one framework, one architecture, or one process. The default is pragmatic delivery over rigid uniformity.

### III. Python Virtual Environments Are Required
All Python code, scripts, tests, and automation MUST run inside a project-local Python virtual environment. Dependencies are installed into the venv, not globally, and commands should be executed from a venv-activated shell or an equivalent project-scoped environment. This keeps local work reproducible and prevents one task from contaminating another.

### IV. Safe Experimentation, Minimal Waste
Temporary work, prototypes, and disposable environments are allowed when they support rapid learning, but they must be kept scoped, documented when needed, and cleaned up promptly. Secrets, credentials, and PII must not be checked in, exposed in logs, or left in shared artifacts.

## Additional Constraints

This project intentionally avoids heavyweight rules. The standard is simple: use the least process that gets the job done, keep the environment clean, and protect sensitive data. If a requirement creates more friction than value, it should be simplified or removed rather than enforced.

## Development Workflow

- Start with the smallest useful prototype or proof of concept.
- Update the repo as the work evolves, without waiting for perfect architecture.
- Run code and tests from the project venv before considering a task complete.
- Keep temporary artifacts short-lived and remove them when no longer needed.
- Keep decisions easy to explain and easy to revisit.

## Governance

This constitution governs the project’s default operating style. The team may adapt the exact implementation details as long as the core priorities remain intact: fast iteration, practical flexibility, and a clean Python venv-based environment. Changes to this constitution require a brief note explaining why the new direction improves delivery or safety. Compliance is checked by ensuring work remains understandable, reproducible, and executable in the project environment.

**Version**: 1.0.0 | **Ratified**: 2026-09-24 | **Last Amended**: 2026-09-24

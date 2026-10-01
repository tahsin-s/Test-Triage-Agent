# Test Triage Agent, Idea and Scope

Problem message from client:

Looking for Agentic QE capabilities for her team/line of work


60% of defects or missteps detected after release are due to lack of prior testing.


Ann's team does UAT, E2E and regression testing every day. She would like for reports to be created every day to then present to Dev Leads.


In order to generate these reports, she would like an agent to work in an IDE, test what is needed (whether an app or just a feature), and destroy the work done by end of day in order to save XXX storage.
Equipping everyone with a VM is too much money, Ann wants to know our capability to do something like this.

### Rewritten

We want testing to be ran from an agent within an IDE, that means that any test-related decisions that need to be made, that usually need a human, don't need to pass through the QA team. It can be done in a hurry, from the developer side.

Components:

- Input (Test collateral, work-product diffs, codebase diffs, summary of prior days)
- Output (Charts where appropriate, important metrics, a crisp 3-5 points bullet points highlighting important updates)
- Workflow integration (one time link with randomized url, ms loops)

Constraints:

- Should not leak PII, or credentials/api-keys stored in .env files
- Should be removed and inaccessible after 24 hours.

## POC Scope

Build the app, and the test suite in a vm. (Manually is fine for now)

Run the test-suite with a shell script.

Attach the shell script to an agent in VS-code

Find a way to sell it

## Code

git repo: https://github.com/JhongFDM/banking-platform.git

active development branch: feature/springai

test-suite branch: QA 
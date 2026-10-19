#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/trigger-triage-workflow.sh [branch] [tags] [max_tags] [dry_run]

Examples:
  ./scripts/trigger-triage-workflow.sh main "@smoke,@auth,@goals" 3 false
  ./scripts/trigger-triage-workflow.sh feature/test "@auth,@goals" 2 true

This dispatches the GitHub Actions workflow using the GitHub CLI.
The workflow file must exist on the target branch and GitHub Actions must be enabled.
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required but was not found in PATH." >&2
  echo "Install it from https://cli.github.com/ and run 'gh auth login'." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

BRANCH="${1:-main}"
TAGS="${2:-@smoke,@auth,@goals}"
MAX_TAGS="${3:-3}"
DRY_RUN="${4:-false}"

if ! [[ "$MAX_TAGS" =~ ^[0-9]+$ ]]; then
  echo "max_tags must be a number, got: $MAX_TAGS" >&2
  exit 1
fi

echo "Dispatching workflow run for branch: $BRANCH"
echo "Tags: $TAGS"
echo "Max tags: $MAX_TAGS"
echo "Dry run: $DRY_RUN"

gh workflow run triage-playwright.yml \
  --ref "$BRANCH" \
  -f branch="$BRANCH" \
  -f tags="$TAGS" \
  -f max_tags="$MAX_TAGS" \
  -f dry_run="$DRY_RUN"

echo
echo "To watch the newest run:"
echo "  gh run watch --workflow triage-playwright.yml"
echo "To list recent runs:"
echo "  gh run list --workflow triage-playwright.yml --limit 5"

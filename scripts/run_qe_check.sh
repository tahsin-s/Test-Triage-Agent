#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${1:-$PWD}"
COMMAND="${2:-pytest -q}"

if [ ! -d "$REPO_PATH" ]; then
  echo "Repository path not found: $REPO_PATH" >&2
  exit 1
fi

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null
python src/qe_agent_cli.py "$REPO_PATH" --command "$COMMAND"

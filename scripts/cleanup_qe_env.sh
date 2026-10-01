#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-$PWD}"

if [ -d "$TARGET_DIR/.venv" ]; then
  rm -rf "$TARGET_DIR/.venv"
fi

find "$TARGET_DIR" -type d -name "qe-run-*" -exec rm -rf {} + 2>/dev/null || true

echo "Temporary QE environment cleaned up."

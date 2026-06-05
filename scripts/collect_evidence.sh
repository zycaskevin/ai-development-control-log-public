#!/usr/bin/env bash
# Generate a v0.2 Control Log evidence snippet from the current working tree.
# Usage: bash scripts/collect_evidence.sh [BASE_REF]
# Default BASE_REF = main.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_REF="${1:-main}"
python3 "$REPO_DIR/scripts/collect_evidence.py" --repo "$REPO_DIR" --base "$BASE_REF"

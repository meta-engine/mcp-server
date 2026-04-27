#!/usr/bin/env bash
# Create the venv used by tools/plot.py and install matplotlib.
# Idempotent — re-running is safe.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
VENV="$ROOT/.venv"

if [ ! -d "$VENV" ]; then
  echo "Creating venv at $VENV..."
  python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet matplotlib

echo "Charts ready. Generate with:"
echo "  $VENV/bin/python $ROOT/tools/plot.py"

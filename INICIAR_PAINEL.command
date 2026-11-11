#!/bin/zsh
# Infinity AI Local Dev Panel — double-click launcher for macOS.
set -e
cd -- "$(dirname -- "$0")"
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
else
  PY="$(command -v python3)"
fi
exec "$PY" tools/local-panel/server.py

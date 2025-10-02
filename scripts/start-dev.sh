#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Create venv if missing
if [ ! -d "venv" ]; then
  echo "Creating virtualenv..."
  python3 -m venv venv
fi

# Activate
# shellcheck source=/dev/null
source venv/bin/activate

# Install dependencies (fast, skip if already satisfied)
pip install --upgrade pip
pip install -r requirements.txt

# Run the launcher using venv python
venv/bin/python run.py

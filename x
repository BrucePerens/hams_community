#!/bin/bash
# Copyright © Bruce Perens K6BP. All Rights Reserved.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON=".venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

echo "========================================================"
echo " 🎨 RUNNING BLACK FORMATTER"
echo "========================================================"

# Execute Black formatting across the directory, skipping isolated environments
"$VENV_PYTHON" -m black "$DIR" --exclude "/(\.venv|venv|env|\.git|__pycache__|node_modules)/"

echo "✅ Formatting complete."

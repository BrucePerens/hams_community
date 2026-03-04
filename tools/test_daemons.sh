#!/bin/bash
# Copyright © Bruce Perens K6BP. All Rights Reserved.
# Centralized test runner for all isolated standalone daemons.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

echo "========================================================"
echo " 🧪 RUNNING ISOLATED DAEMON TESTS"
echo "========================================================"

cd "$DIR/daemons"
"$VENV_PYTHON" -m unittest discover -s . -p "test_*.py" -v

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Some daemon tests failed."
    exit 1
else
    echo "✅ All daemon tests passed successfully."
    exit 0
fi

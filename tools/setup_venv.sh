#!/bin/bash
# Copyright © Bruce Perens K6BP. All Rights Reserved.
# Provisions the unified root Python virtual environment for Odoo tools and Daemons.

# Safely get the absolute path to the repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "[*] Initializing root Python virtual environment at $ROOT_DIR/.venv..."
python3 -m venv .venv

echo "[*] Upgrading pip..."
.venv/bin/python -m pip install --upgrade pip

echo "[*] Installing all platform dependencies from $ROOT_DIR/requirements.txt..."
.venv/bin/pip install -r requirements.txt

echo "[+] Unified virtual environment successfully created at $ROOT_DIR/.venv"
echo "[*] To activate manually, run: source .venv/bin/activate"

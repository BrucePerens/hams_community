#!/bin/bash
# Copyright © Bruce Perens K6BP. All Rights Reserved.
# Centralized linter execution script. Silent on success.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"
VENV_PYTHON="$DIR/.venv/bin/python"

LINTERS_FAILED=0

if [ ! -f "$VENV_PYTHON" ]; then
    bash "$DIR/tools/setup_venv.sh" > /dev/null 2>&1
fi

# 0. Pre-Flight Dependency Checks
TARGET_MODULES="${1:-}"
if [ -n "$TARGET_MODULES" ]; then
    IFS=',' read -ra MOD_ARRAY <<< "$TARGET_MODULES"
    for MOD in "${MOD_ARRAY[@]}"; do
        if [ -f "$DIR/$MOD/__manifest__.py" ]; then
            MOD_PATH="$DIR/$MOD"
        elif [ -f "$COMMUNITY_DIR/$MOD/__manifest__.py" ]; then
            MOD_PATH="$COMMUNITY_DIR/$MOD"
        else
            continue
        fi
        
        OUT="$("$VENV_PYTHON" "$DIR/tools/pre_flight_check.py" -m "$MOD_PATH" --addons-path "$ADDONS_PATH" 2>&1)"
        if [ $? -ne 0 ]; then
            echo "$OUT"
            LINTERS_FAILED=1
        fi
    done
fi

# 1. Flake8
if command -v flake8 >/dev/null 2>&1 || [ -f "$DIR/.venv/bin/flake8" ]; then
    FLAKE8_CMD="flake8"
    [ -f "$DIR/.venv/bin/flake8" ] && FLAKE8_CMD="$DIR/.venv/bin/flake8"
    
    OUT="$("$FLAKE8_CMD" "$DIR" --exclude=venv,env,.venv,__pycache__,node_modules --select=E9,F --per-file-ignores="__init__.py:F401" 2>&1)"
    if [ $? -ne 0 ]; then
        echo "❌ Flake8 Violations:"
        echo "$OUT"
        LINTERS_FAILED=1
    fi
fi

# 2. Burn List Linter
OUT="$("$VENV_PYTHON" "$DIR/tools/check_burn_list.py" "$DIR" 2>&1)"
if [ $? -ne 0 ]; then
    echo "$OUT"
    LINTERS_FAILED=1
elif [ -n "$OUT" ]; then
    echo "$OUT"
fi

# 3. Semantic Anchors Verification
# Pass both private and community directories to resolve cross-repository anchor links
OUT="$("$VENV_PYTHON" "$DIR/tools/verify_anchors.py" "$DIR" "$COMMUNITY_DIR" 2>&1)"
if [ $? -ne 0 ]; then
    echo "$OUT"
    LINTERS_FAILED=1
elif [ -n "$OUT" ]; then
    echo "$OUT"
fi

if [ $LINTERS_FAILED -ne 0 ]; then
    echo "🛑 Halting due to linter violations. Please review the output above."
    exit 1
else
    exit 0
fi

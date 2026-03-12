#!/bin/bash
# Fast XML Compilation Check
# Iterates through all custom modules and updates them one by one without running the test suite.
# This triggers Odoo's native QWeb compiler to quickly surface XPath/Inheritance ParseErrors.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

VENV_PYTHON="$DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

DB_NAME="${1:-hams_test}"

if [ -f "$DIR/default_modules.txt" ]; then
    IFS=',' read -r -a MODULES <<< "$(cat "$DIR/default_modules.txt")"
else
    MODULES=($(find "$DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; | awk -F/ '{print $NF}'))
fi

echo "========================================================"
echo " ⚡ FAST XML COMPILATION CHECK"
echo " Target Database: $DB_NAME"
echo "========================================================"

FAILED_MODULES=()

for MOD in "${MODULES[@]}"; do
    if [ -f "$DIR/$MOD/__manifest__.py" ]; then
        echo -e "\n[*] Checking XML views in: $MOD"
        # Run the update command, capture stderr, stop after init, no tests
        export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"
        "$VENV_PYTHON" /usr/bin/odoo --addons-path="$ADDONS_PATH" -d "$DB_NAME" -i "$MOD" -u "$MOD" --stop-after-init --log-level=error
        
        if [ $? -ne 0 ]; then
            echo "❌ ERROR: XML compilation failed in $MOD!"
            FAILED_MODULES+=("$MOD")
        else
            echo "✅ $MOD passed."
        fi
    fi
done

echo -e "\n========================================================"
if [ ${#FAILED_MODULES[@]} -eq 0 ]; then
    echo "🎉 All modules compiled successfully!"
    exit 0
else
    echo "🚨 The following modules have XML compilation errors:"
    for FMOD in "${FAILED_MODULES[@]}"; do
        echo "   - $FMOD"
    done
    exit 1
fi

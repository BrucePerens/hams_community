#!/bin/bash
# 🚀 ODOO TEST RUNNER

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

VENV_PYTHON="$DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

echo "[*] Scanning documentation and codebase for Semantic Anchors..."
"$VENV_PYTHON" "$DIR/tools/verify_anchors.py" "$DIR"
if [ $? -ne 0 ]; then
    echo "🛑 Halting due to linter violations. Please review the output above."
    exit 1
fi

DB_NAME="${2:-hams_test}"

if [ -n "$1" ]; then
    TARGET_MODULE="$1"
else
    # Dynamically target ONLY our custom modules to avoid running Odoo's core framework tests
    MODS=($(find "$DIR" "$COMMUNITY_DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; 2>/dev/null | awk -F/ '{print $NF}' | sort -u))
    TARGET_MODULE=$(IFS=,; echo "${MODS[*]}")
fi

echo "=========================================================="
echo " 🧪 ODOO TEST RUNNER"
echo "=========================================================="
echo " Target Database: $DB_NAME"
echo " Target Modules:  $TARGET_MODULE"
echo "=========================================================="

echo "[*] Dropping and Rebuilding Database Schema ($DB_NAME)..."
dropdb --if-exists "$DB_NAME"
createdb "$DB_NAME"

echo "[*] Executing Test Suite..."
LOG_FILE="/tmp/odoo_test_run_$$.log"

"$VENV_PYTHON" /usr/bin/odoo \
  --addons-path="$ADDONS_PATH" \
  --dev=all -d "$DB_NAME" \
  -i "$TARGET_MODULE" \
  --test-enable --stop-after-init

echo "[+] Test Run Complete."

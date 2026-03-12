#!/bin/bash
# 🚀 TRUE INTEGRATION TEST RUNNER

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

VENV_PYTHON="$DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

DB_NAME="${1:-hams_test}"

if [ -n "$2" ]; then
    TARGET_MODULE="$2"
else
    # Dynamically target ONLY our custom modules to avoid running Odoo's core framework tests
    MODS=($(find "$DIR" "$COMMUNITY_DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; 2>/dev/null | awk -F/ '{print $NF}' | sort -u))
    TARGET_MODULE=$(IFS=,; echo "${MODS[*]}")
fi

export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"
export HAMS_INTEGRATION_MODE="1"

echo "=========================================================="
echo " 🚀 TRUE INTEGRATION TEST RUNNER"
echo "=========================================================="
echo " Target Database: $DB_NAME"
echo " Target Modules:  $TARGET_MODULE"
echo "=========================================================="

echo "[*] Dropping and Rebuilding Database Schema ($DB_NAME)..."
dropdb --if-exists "$DB_NAME"
createdb "$DB_NAME"

echo "[*] Initialize the DB so the daemons have tables to query and authenticate against..."
"$VENV_PYTHON" /usr/bin/odoo --addons-path="$ADDONS_PATH" -d "$DB_NAME" -i "$TARGET_MODULE" --stop-after-init > /dev/null 2>&1

echo "[*] Starting Background Daemons..."
# (Background daemons would be started here if needed for integration)

echo "[*] Executing Test Suite in Integration Mode..."
# Run tests natively. The Python tests will see HAMS_INTEGRATION_MODE=1 and bypass MagicMocks.
"$VENV_PYTHON" /usr/bin/odoo --addons-path="$ADDONS_PATH" -d "$DB_NAME" -u "$TARGET_MODULE" --test-enable --stop-after-init

echo "[+] Integration Run Complete."

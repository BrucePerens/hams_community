#!/bin/bash
# Copyright © Bruce Perens K6BP. All Rights Reserved.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

echo "=========================================================="
echo " 🚀 TRUE INTEGRATION TEST RUNNER"
echo "=========================================================="

# 1. Set the global toggle so Python tests know to disable MagicMocks
export HAMS_INTEGRATION_MODE=1

if [ -z "$1" ]; then
    if [ -f "$DIR/default_modules.txt" ]; then
        TARGET_MODULE=$(cat "$DIR/default_modules.txt)
    else
        TARGET_MODULE=$(find "$DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; | awk -F/ '{print $NF}' | paste -sd "," -)
    fi
else
    TARGET_MODULE="$1"
fi

DB_NAME="test_integration_${TARGET_MODULE//,/_}"
DB_NAME="${DB_NAME:0:63}"

# 2. Expose credentials for the standalone daemons
export ODOO_DB="$DB_NAME"
export DB_NAME="$DB_NAME"
export ODOO_SERVICE_PASSWORD=$(openssl rand -hex 24)

VENV_PYTHON="$DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

echo "[*] Dropping and Rebuilding Database Schema ($DB_NAME)..."
dropdb --if-exists "$DB_NAME" || true
createdb "$DB_NAME"

# 3. Initialize the DB so the daemons have tables to query and authenticate against
/usr/bin/odoo --addons-path="$ADDONS_PATH" -d "$DB_NAME" -i "$TARGET_MODULE" --stop-after-init > /dev/null 2>&1

echo "[*] Starting Background Daemons..."
# (Background daemons would be started here if needed for integration)

echo "[*] Executing Test Suite in Integration Mode..."
# Run tests natively. The Python tests will see HAMS_INTEGRATION_MODE=1 and bypass MagicMocks.
/usr/bin/odoo --addons-path="$ADDONS_PATH" -d "$DB_NAME" -u "$TARGET_MODULE" --test-enable --stop-after-init
TEST_EXIT=$?

echo "[*] Tearing down Daemons..."
# (Daemons would be killed here)

echo "[*] Cleaning up test database..."
dropdb --if-exists "$DB_NAME" || true

exit $TEST_EXIT

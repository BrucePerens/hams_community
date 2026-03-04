#!/bin/bash

# Resolve project root dynamically based on script location
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

# Allow passing a target module to test, with defaults.
if [ -z "$1" ]; then
    if [ -f "$DIR/default_modules.txt" ]; then
        TARGET_MODULE=$(cat "$DIR/default_modules.txt")
    else
        TARGET_MODULE=$(find "$DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; | awk -F/ '{print $NF}' | paste -sd "," -)
    fi
else
    TARGET_MODULE="$1"
fi

DB_NAME="test_${TARGET_MODULE//,/_}"
DB_NAME="${DB_NAME:0:63}" # Truncate to PostgreSQL's 63-byte identifier limit

# If the user passed additional arguments (like --test-tags simulation), use those.
# Otherwise, default to testing all tests in the target modules.
if [ -z "$2" ]; then
    TEST_ARGS="--test-tags /${TARGET_MODULE//,/,/},-simulation"
else
    TEST_ARGS="${@:2}"
fi

# Generate an ephemeral secure password for the test environment
export ODOO_SERVICE_PASSWORD=$(openssl rand -hex 24)

VENV_PYTHON="$DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[*] Common virtual environment not found. Building it now..."
    bash "$DIR/tools/setup_venv.sh"
fi

bash "$DIR/tools/run_linters.sh" "$TARGET_MODULE"
if [ $? -ne 0 ]; then
    exit 1
fi

# (Silent success) Booting DB ($DB_NAME) and running tests...

# Use BOTH -i and -u.
# -i ensures missing modules install into the DB.
# -u ensures existing modules reload their Python code (and tests) from disk.
LOG_FILE="/tmp/odoo_test_run_$$.log"
/usr/bin/odoo \
  --addons-path="$ADDONS_PATH" \
  -d "$DB_NAME" \
  -i "$TARGET_MODULE" \
  -u "$TARGET_MODULE" \
  --test-enable \
  $TEST_ARGS \
  --stop-after-init | tee "$LOG_FILE"

ODOO_EXIT=${PIPESTATUS[0]}

if grep -q " 0 failed, 0 error(s) of 0 tests" "$LOG_FILE"; then
    echo "\n\ud83d\uded1 Halting: 0 tests were executed. This indicates a dependency loop or syntax error preventing the module from loading."
    rm -f "$LOG_FILE"
    exit 1
fi

if grep -q "ERROR .* Some modules are not loaded" "$LOG_FILE"; then
    echo "\n\ud83d\uded1 Halting: Modules failed to load (Dependency Loop detected)."
    rm -f "$LOG_FILE"
    exit 1
fi

rm -f "$LOG_FILE"
exit $ODOO_EXIT

#!/bin/bash

# Resolve project root dynamically based on script location
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMUNITY_DIR="$(cd "$DIR/../hams_community" && pwd 2>/dev/null || echo "$DIR/../hams_community")"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR,$COMMUNITY_DIR"

# Allow passing a target module to test, with defaults.
TARGET_MODULE="${1:-manual_library,compliance,user_websites}"

# If the user passed additional arguments (like --test-tags simulation), use those.
# Otherwise, default to testing all tests in the target modules.
if [ -z "$2" ]; then
    TEST_ARGS="--test-tags /${TARGET_MODULE//,/,/}"
else
    TEST_ARGS="${@:2}"
fi

# Generate an ephemeral secure password for the test environment
export ODOO_SERVICE_PASSWORD=$(openssl rand -hex 24)

echo "🚀 Running Pre-Flight Check for ${TARGET_MODULE}..."
if [ -d "$DIR/$TARGET_MODULE" ]; then
    python3 "$DIR/tools/pre_flight_check.py" -m "$DIR/$TARGET_MODULE" --addons-path "$ADDONS_PATH"
    if [ $? -ne 0 ]; then
        echo "🛑 Halting startup due to pre-flight check failure."
        exit 1
    fi
fi

echo "🔥 Running Odoo 19+ Burn List & Syntax Check..."
python3 "$DIR/tools/check_burn_list.py" "$DIR"
if [ $? -ne 0 ];
then
    echo "🛑 Halting startup due to Syntax or Burn List violations. Please review the output above."
exit 1
fi

echo "⚓ Running Semantic Anchor Traceability Check..."
python3 "$DIR/tools/verify_anchors.py"
if [ $? -ne 0 ];
then
    echo "🛑 Halting startup due to missing Semantic Anchors. Please restore them."
exit 1
fi

echo "🧪 Pre-flight, Syntax, and Anchor checks passed. Booting DB and running tests..."

# Use BOTH -i and -u.
# -i ensures missing modules install into the DB.
# -u ensures existing modules reload their Python code (and tests) from disk.
/usr/bin/odoo \
  --addons-path="$ADDONS_PATH" \
  -d db1 \
  -i "$TARGET_MODULE" \
  -u "$TARGET_MODULE" \
  --test-enable \
  $TEST_ARGS \
  --stop-after-init

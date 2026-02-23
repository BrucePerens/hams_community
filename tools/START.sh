#!/bin/bash

# Resolve project root dynamically based on script location
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,$DIR"

# Allow passing a target module to test (defaults to user_websites)
TARGET_MODULE="${1:-user_websites}"

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

echo "🔥 Running Odoo 19+ Burn List Check..."
python3 "$DIR/tools/check_burn_list.py" "$DIR"
if [ $? -ne 0 ]; then
    echo "🛑 Halting startup due to Burn List violations. Please review the output above."
    exit 1
fi

echo "🧪 Pre-flight and Burn List checks passed. Rebuilding database and running tests for ${TARGET_MODULE}..."

# Use --if-exists to prevent halting if the database was previously deleted manually
runuser -u odoo -- dropdb --if-exists db1
runuser -u odoo -- \
  /usr/bin/odoo -c /etc/odoo/odoo.conf \
  --addons-path="$ADDONS_PATH" \
  --dev=all -d db1 \
  -i base,$TARGET_MODULE \
  --test-enable \
  --test-tags /$TARGET_MODULE \
  --stop-after-init

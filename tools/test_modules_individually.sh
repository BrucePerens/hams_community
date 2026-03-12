#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$DIR/default_modules.txt" ]; then
    IFS=',' read -r -a MODULES <<< "$(cat "$DIR/default_modules.txt)"
else
    MODULES=($(find "$DIR" -maxdepth 2 -name "__manifest__.py" -exec dirname {} \; | awk -F/ '{print $NF}'))
fi

echo "========================================================"
echo " 🧪 INDIVIDUAL MODULE TEST RUNNER"
echo "========================================================"

FAILED_MODULES=()

for MOD in "${MODULES[@]}"; do
    if [ -f "$DIR/$MOD/__manifest__.py" ]; then
        echo -e "\n[*] ----------------------------------------------------"        echo "[*] Testing Module: $MOD"
        echo "[*] ----------------------------------------------------"
        
        # Call START.sh with the specific module to force a clean DB per module
        bash "$DIR/tools/START.sh" "$MOD"
        
        if [ $? -ne 0 ]; then
            echo "❌ ERROR: Tests failed for $MOD!"
            FAILED_MODULES+=("$MOD")
        else
            echo "✅ $MOD passed successfully."
        fi
    fi
done

echo -e "\n========================================================"
if [ ${#FAILED_MODULES[@]} -eq 0 ]; then
    echo "🎉 All modules passed individual testing!"
    exit 0
else
    echo "🚨 The following modules failed testing:"
    for FMOD in "${FAILED_MODULES[@]}"; do
        echo "   - $FMOD"
    done
    exit 1
fi

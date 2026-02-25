#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================================="
echo " ⏳ Initiating 1-Hour Full Platform Simulation"
echo "=========================================================="
echo "[*] Setting environment variable SIMULATION_DURATION_MINUTES=60"
export SIMULATION_DURATION_MINUTES=60

"$DIR/tools/RUN.sh" user_websites --test-tags simulation

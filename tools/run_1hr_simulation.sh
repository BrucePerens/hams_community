#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================================="
echo " ⏳ Initiating 1-Hour Full Platform Simulation"
echo "=========================================================="
echo "[*] Setting environment variable SIMULATION_DURATION_MINUTES=60"
export SIMULATION_DURATION_MINUTES=300

"$DIR/tools/RUN.sh" cloudflare,user_websites,user_websites_seo --test-tags simulation

#!/bin/bash
# Synchronizes abstracted core tools and documentation to the open-source community repository.

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$(cd "$SOURCE_DIR/../hams_community" && pwd 2>/dev/null)"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Error: hams_community directory not found at $SOURCE_DIR/../hams_community"
    exit 1
fi

echo "🔄 Synchronizing to Community Repository..."

# 1. Sync Tools (Excluding private configs)
echo "📂 Syncing tools/..."
rsync -av --delete --exclude 'default_modules.txt' --exclude 'tier_config.json' "$SOURCE_DIR/tools/" "$TARGET_DIR/tools/"

# 2. Sync Core Documentation Boundaries
echo "📂 Syncing docs/core/ boundaries..."
DOC_CATEGORIES=("adrs" "runbooks" "stories" "journeys" "security_models" "modules")

for CAT in "${DOC_CATEGORIES[@]}"; do
    if [ -d "$SOURCE_DIR/docs/$CAT/core" ]; then
        mkdir -p "$TARGET_DIR/docs/$CAT/core"
        rsync -av --delete "$SOURCE_DIR/docs/$CAT/core/" "$TARGET_DIR/docs/$CAT/core/"
    fi
done

# 3. Sync Global Project Requirements
echo "📄 Syncing global LLM instructions and System Guides..."
cp "$SOURCE_DIR"/docs/LLM_*.md "$TARGET_DIR"/docs/ 2>/dev/null || true
cp "$SOURCE_DIR"/docs/SYSTEM_*.md "$TARGET_DIR"/docs/ 2>/dev/null || true
cp "$SOURCE_DIR"/docs/COMPARED_TO_ODOO.md "$TARGET_DIR"/docs/ 2>/dev/null || true

echo "✅ Synchronization complete! The hams_community repository has been updated safely."

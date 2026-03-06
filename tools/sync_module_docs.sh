#!/bin/bash
# Synchronizes LLM_DOCUMENTATION.md files from modules into docs/modules

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_MOD_DIR="$ROOT_DIR/docs/modules"

mkdir -p "$DOCS_MOD_DIR"

echo "Synchronizing LLM Documentation..."

find "$ROOT_DIR" -maxdepth 2 -name "LLM_DOCUMENTATION.md" | while read -r FILE_PATH; do
    MOD_DIR=$(dirname "$FILE_PATH")
    MOD_NAME=$(basename "$MOD_DIR")
    
    if [ "$MOD_NAME" != "docs" ] && [ "$MOD_NAME" != "tools" ]; then
        TARGET_PATH="$DOCS_MOD_DIR/${MOD_NAME}.md"
        cp "$FILE_PATH" "$TARGET_PATH"
        echo "✅ Synced $MOD_NAME -> $TARGET_PATH"
    fi
done

echo "Synchronization complete!"

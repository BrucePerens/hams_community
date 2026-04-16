#!/bin/bash
# Automatically syncs LLM_DOCUMENTATION.md files to the docs/modules/ directory.
# Discovers module names dynamically from their directory structures.

set -e

DOCS_DIR="docs/modules"
mkdir -p "$DOCS_DIR"

echo "Syncing LLM_DOCUMENTATION.md files..."

find . -type f -name "LLM_DOCUMENTATION.md" -not -path "./docs/*" | while read -r doc_file; do
    mod_dir=$(dirname "$doc_file")
    mod_name=$(basename "$mod_dir")

    cp "$doc_file" "$DOCS_DIR/${mod_name}.md"
    echo "  -> Synced: $mod_name.md"
done

echo "Sync complete."

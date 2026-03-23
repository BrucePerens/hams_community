#!/bin/bash
# tools/merge_repos.sh

echo "[*] Initiating repository merge..."

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEC_DIR="$(cd "$BASE_DIR/../hams_private_secondary" 2>/dev/null && pwd)"
TER_DIR="$(cd "$BASE_DIR/../hams_private_tertiary" 2>/dev/null && pwd)"

merge_modules() {
    local src_dir=$1
    if [ -n "$src_dir" ] && [ -d "$src_dir" ]; then
        echo "[*] Scanning $src_dir for Odoo modules..."
        for mod_path in "$src_dir"/*/; do
            # Strip the trailing slash and check if it's a symlink
            if [ -L "${mod_path%/}" ]; then
                continue # Explicitly skip symlinks like docs/, tools/, etc.
            fi

            if [ -f "${mod_path}__manifest__.py" ]; then
                mod_name=$(basename "$mod_path")
                echo "  -> Moving module: $mod_name"
                mv "$mod_path" "$BASE_DIR/"
            fi
        done
        
        echo "  -> Cleaning up remaining symlinks and removing $src_dir..."
        rm -rf "$src_dir"
    else
        echo "[-] Source directory $src_dir not found. Skipping."
    fi
}

merge_modules "$SEC_DIR"
merge_modules "$TER_DIR"

echo "[+] Modules successfully merged into the primary repository."
echo "[+] Secondary and Tertiary directories have been removed."

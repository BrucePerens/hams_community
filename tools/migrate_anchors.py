#!/usr/bin/env python3
import os
import sys


def migrate_anchors(root_dir):
    """
    Recursively scans the repository to replace the legacy Semantic Anchor format.
    Transitions '[%ANCHOR:' to '[@ANCHOR:' across all code, XML, and documentation.
    """
    # Safe extensions to target for text replacements
    target_exts = (
        ".py",
        ".js",
        ".xml",
        ".html",
        ".md",
        ".csv",
        ".yaml",
        ".yml",
        ".txt",
        ".sh",
    )

    # Directories to safely ignore
    exclude_dirs = {".git", "venv", "__pycache__", "node_modules", ".tox", "hams_bin"}

    changed_files_count = 0

    print("[*] Starting Semantic Anchor Migration: '[%ANCHOR:' -> '[@ANCHOR:'")

    for root, dirs, files in os.walk(root_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if not file.endswith(target_exts):
                continue

            full_path = os.path.join(root, file)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # A direct string replacement will safely catch standard usage:
                #   [@ANCHOR: name] -> [@ANCHOR: name]
                # As well as the raw regex patterns inside verify_anchors.py:
                #   r"\[@ANCHOR:\s*..." -> r"\[@ANCHOR:\s*..."
                if "[%ANCHOR" in content:
                    new_content = content.replace("[%ANCHOR", "[@ANCHOR")

                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    changed_files_count += 1
                    print(f"  [+] Updated: {full_path}")

            except UnicodeDecodeError:
                # Gracefully skip any binary files masquerading with text extensions
                pass

    print(
        f"\n[+] Migration complete. Successfully updated {changed_files_count} files."
    )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    migrate_anchors(target)

#!/usr/bin/env python3
import os
import logging

# Initialize a basic logger for the linter requirements
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_imports(root_dir):
    replacements = [
        ("from odoo.addons.hams_test.tests.common import", "from odoo.addons.hams_test.tests.common import"),
        ("import odoo.addons.hams_test.tests.common", "import odoo.addons.hams_test.tests.common")
    ]

    modified_count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        # Skip typical isolated/cache directories to speed up execution
        if any(ignored in dirpath for ignored in [".venv", "__pycache__", ".git", "node_modules"]):
            continue

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    new_content = content
                    for old_str, new_str in replacements:
                        new_content = new_content.replace(old_str, new_str)

                    if new_content != content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"[+] Updated imports in: {os.path.relpath(filepath, root_dir)}")
                        modified_count += 1
                except Exception as e:  # audit-ignore-catch-all
                    # Required by AST Burn List Linter to prevent silent failures
                    logger.warning("Could not process %s: %s", filepath, e)
                    print(f"[!] Could not process {filepath}: {e}")

    print(f"\nDone! Successfully modified {modified_count} files.")

if __name__ == "__main__":
    # Resolve the repository root (one level up from tools/)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"[*] Scanning repository for legacy hams_test imports at: {repo_root}")
    fix_imports(repo_root)

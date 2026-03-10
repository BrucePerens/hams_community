#!/usr/bin/env python3
import os
import re


def purge_bypass_tag():
    print("[*] Purging obsolete 'burn-ignore-test-commit' bypass from workspace...")
    target_exts = (".md", ".sh", ".py", ".txt")

    for root, dirs, files in os.walk("."):
        # Skip hidden directories like .git or .venv
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if not file.endswith(target_exts) or file == os.path.basename(__file__):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            if "burn-ignore-test-commit" in content:
                print(f"  [-] Removing references from: {filepath}")

                # 1. Strip from shell script greps (e.g., `| grep -v "burn-ignore-test-commit"`)
                content = re.sub(
                    r'\|\s*grep\s+-v\s+["\']?burn-ignore-test-commit["\']?', "", content
                )

                # 2. Strip from Python linter lists/strings and documentation text
                lines = content.split("\n")
                new_lines = [
                    line for line in lines if "burn-ignore-test-commit" not in line
                ]

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

    print(
        "[+] Purge complete. The linter will now strictly fail any unauthorized .commit() calls."
    )


if __name__ == "__main__":
    purge_bypass_tag()

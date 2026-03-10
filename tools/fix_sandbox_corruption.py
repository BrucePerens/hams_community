#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reverts collateral damage caused by the sandbox enforcer matching substrings
inside 'ham_base.group_user_manager_service'.
"""

import os


def fix_corruption():
    count = 0
    for root, dirs, files in os.walk("."):
        if any(
            ignored in root.split(os.sep)
            for ignored in [
                ".git",
                "venv",
                "env",
                "__pycache__",
                "node_modules",
                "docs",
                "tools",
            ]
        ):
            continue

        for file in files:
            if file.endswith((".xml", ".csv", ".py")):
                filepath = os.path.join(root, file)

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                if "ham_base.group_portal" in content:
                    new_content = content.replace(
                        "ham_base.group_portal", "ham_base.group_user"
                    )
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"🔧 Fixed collateral damage in: {filepath}")
                    count += 1

    print(f"\n✅ Restored {count} files.")


if __name__ == "__main__":
    fix_corruption()

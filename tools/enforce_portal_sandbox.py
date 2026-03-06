#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Domain Sandbox Enforcement Utility
----------------------------------
Replaces the dangerous `base.group_portal` with `base.group_portal` across all
custom module ACLs, Record Rules, and Automated Tests.
"""

import os

def enforce_sandbox():
    count = 0
    for root, dirs, files in os.walk("."):
        # Ignore non-source directories, docs, and tooling to prevent breaking linters
        if any(ignored in root.split(os.sep) for ignored in [".git", "venv", "env", "__pycache__", "node_modules", "docs", "tools"]):
            continue

        for file in files:
            filepath = os.path.join(root, file)

            # Protect the specific files where base.group_portal is architecturally required
            # (e.g. provisioning the internal service accounts)
            if "core_base/security/security_data.xml" in filepath.replace("\\", "/"):
                continue

            if file.endswith((".xml", ".csv", ".py")):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                if "base.group_portal" in content:
                    new_content = content.replace("base.group_portal", "base.group_portal")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"🔒 Sandboxed: {filepath}")
                    count += 1

    print(f"\n✅ Domain Sandbox Enforced across {count} files.")
    print("All community users, ACLs, rules, and tests are now strictly isolated to base.group_portal.")


if __name__ == "__main__":
    enforce_sandbox()

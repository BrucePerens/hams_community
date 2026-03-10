#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re


def fix_tests():
    for root, _, files in os.walk("."):
        if "venv" in root or ".git" in root:
            continue
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            changed = False

            # 1. Fix groups_web/ham/swl disjoint logic crashes
            for grp in ["web", "ham", "swl"]:
                old_str = f'groups_{grp} = [self.env.ref("base.group_portal").id]\n        if {grp}_grp:\n            groups_{grp}.append({grp}_grp.id)'
                new_str = f'groups_{grp} = []\n        if {grp}_grp:\n            groups_{grp}.append({grp}_grp.id)\n        else:\n            groups_{grp}.append(self.env.ref("base.group_portal").id)'
                if old_str in content:
                    content = content.replace(old_str, new_str)
                    changed = True

                old_str_user = f'groups_{grp} = [self.env.ref("base.group_user").id]\n        if {grp}_grp:\n            groups_{grp}.append({grp}_grp.id)'
                new_str_user = f'groups_{grp} = []\n        if {grp}_grp:\n            groups_{grp}.append({grp}_grp.id)\n        else:\n            groups_{grp}.append(self.env.ref("base.group_user").id)'
                if old_str_user in content:
                    content = content.replace(old_str_user, new_str_user)
                    changed = True

            # 2. Remove ham.operator.index creation (it's now a SQL View)
            idx_create_pattern = (
                r'self\.env\["ham\.operator\.index"\]\.create\(\s*\{[^\}]*\}\s*\)'
            )
            if re.search(idx_create_pattern, content):
                content = re.sub(idx_create_pattern, "self.env.flush_all()", content)
                changed = True

            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed {path}")


if __name__ == "__main__":
    fix_tests()

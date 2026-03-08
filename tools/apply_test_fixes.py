#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re


def fix_tests():
    # Scan parent directory to cover both hams_private and hams_community
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for root, _, files in os.walk(base_dir):
        if (
            "venv" in root
            or ".git" in root
            or "node_modules" in root
            or "__pycache__" in root
        ):
            continue
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

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

            # 3. Remove invalid .clear_cache() calls that break distributed_redis_cache
            # 3. Remove invalid .clear_cache() calls that break distributed_redis_cache
            if ".clear_cache(" in content:
                # Strip lines that call clear_cache on a method, but preserve registry clearing
                new_content = re.sub(
                    r"^[ \t]*(?!self\.env\.registry)[A-Za-z0-9_.]+\.clear_cache\(.*?\)\n",
                    "",
                    content,
                    flags=re.MULTILINE,
                )
                if new_content != content:
                    content = new_content
                    changed = True

            # 4. Inject global shutil.which mock directly into the test modules
            if (
                "test_08d_kopia_auto_download" in content
                or "test_02c_etcd_auto_download" in content
            ) and "shutil._orig_which" not in content:
                injection = "\nimport shutil\nimport os\nif not hasattr(shutil, '_orig_which'):\n    shutil._orig_which = shutil.which\n    shutil.which = lambda cmd, mode=os.F_OK, path=None: None if cmd in ('kopia', 'etcd') else shutil._orig_which(cmd, mode, path)\n"
                if "from odoo.tests.common" in content:
                    content = content.replace(
                        "from odoo.tests.common",
                        injection + "from odoo.tests.common",
                        1,
                    )
                    changed = True

            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed {path}")


if __name__ == "__main__":
    fix_tests()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manifest Dependency Graph & Completeness Linter
Simulates Odoo's XML parsing chronology offline to detect forward references
and broken load-orders. Also enforces manifest completeness (missing XMLs, missing Tours).
"""

import os
import sys
import ast
import re

def check_manifest(base_dir):
    errors = []

    id_def_re = re.compile(r'<(?:record|template|menuitem|act_window)[^>]+id="([^"]+)"')
    ref_attr_re = re.compile(r'\bref="([^"]+)"')
    eval_ref_re = re.compile(r"ref\(['\"]([^'\"]+)['\"]\)")

    for root, dirs, files in os.walk(base_dir):
        if "__manifest__.py" in files:
            manifest_path = os.path.join(root, "__manifest__.py")
            module_name = os.path.basename(root)

            with open(manifest_path, 'r', encoding='utf-8') as f:
                try:
                    manifest_data = ast.literal_eval(f.read())
                except (SyntaxError, ValueError, TypeError) as e:
                    errors.append(f"❌ ERROR: Failed to parse {manifest_path}: {e}")
                    continue

            data_files = manifest_data.get('data', [])
            assets = manifest_data.get('assets', {})
            data_files_set = set(data_files)
            defined_ids = set()

            # --- 1. Manifest Completeness Checks ---
            for dirpath, _, filenames in os.walk(root):
                # Check XML and CSV completeness (skip static and tests for data)
                path_parts = dirpath.replace(base_dir, '').split(os.sep)
                is_static = 'static' in path_parts

                for filename in filenames:
                    # Data Array Completeness
                    if not is_static and (filename.endswith('.xml') or filename == 'ir.model.access.csv'):
                        rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
                        rel_path_fwd = rel_path.replace(os.sep, '/')
                        if rel_path_fwd not in data_files_set:
                            errors.append(f"📄 {module_name}/{rel_path_fwd}\n ❌ CRITICAL: File exists but is NOT registered in the 'data' array of __manifest__.py")

                    # Tour Asset Completeness
                    if is_static and filename.endswith('.js') and 'tours' in path_parts:
                        rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
                        rel_path_fwd = rel_path.replace(os.sep, '/')

                        web_assets_tests = assets.get('web.assets_tests', [])
                        covered = False
                        for asset_path in web_assets_tests:
                            if asset_path == f"{module_name}/{rel_path_fwd}":
                                covered = True
                                break
                            # Glob check
                            if asset_path.endswith('**/*') and asset_path.startswith(f"{module_name}/static/"):
                                glob_base = asset_path.replace('**/*', '')
                                if f"{module_name}/{rel_path_fwd}".startswith(glob_base):
                                    covered = True
                                    break
                            if asset_path.endswith('*.js') and asset_path.startswith(f"{module_name}/static/"):
                                glob_base = asset_path.replace('*.js', '')
                                if f"{module_name}/{rel_path_fwd}".startswith(glob_base):
                                    covered = True
                                    break

                        if not covered:
                            errors.append(f"📄 {module_name}/{rel_path_fwd}\n ❌ CRITICAL: Tour file exists but is NOT registered in 'web.assets_tests' in __manifest__.py")

            # --- 2. Load Order & Forward References Check ---
            for data_file in data_files:
                file_path = os.path.join(root, data_file)
                if not os.path.exists(file_path):
                    continue

                if file_path.endswith('.xml'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            for match in id_def_re.finditer(line):
                                new_id = match.group(1)
                                defined_ids.add(new_id)
                                defined_ids.add(f"{module_name}.{new_id}")

                            refs_to_check = []
                            refs_to_check.extend(ref_attr_re.findall(line))
                            refs_to_check.extend(eval_ref_re.findall(line))

                            for ref_id in refs_to_check:
                                if ref_id.startswith('model_') or ('.' in ref_id and ref_id.split('.')[1].startswith('model_')):
                                    continue

                                if '.' in ref_id:
                                    ref_module, _ = ref_id.split('.', 1)
                                    if ref_module != module_name:
                                        continue

                                if ref_id not in defined_ids:
                                    errors.append(
                                        f"📄 {module_name}/{data_file}:{line_num}\n"
                                        f" ❌ CRITICAL LOAD ORDER: Forward reference detected. '{ref_id}' is referenced before it is defined. "
                                        f"Check the data array sequence in __manifest__.py."
                                    )

                elif file_path.endswith('.csv'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if not lines:
                            continue
                        headers = lines[0].strip().split(',')
                        if 'id' in headers:
                            id_idx = headers.index('id')
                            for line in lines[1:]:
                                parts = line.strip().split(',')
                                if len(parts) > id_idx:
                                    csv_id = parts[id_idx]
                                    defined_ids.add(csv_id)
                                    defined_ids.add(f"{module_name}.{csv_id}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("[+] SUCCESS: Manifest dependencies and completeness validated.")
        sys.exit(0)

if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_manifest(base_dir)

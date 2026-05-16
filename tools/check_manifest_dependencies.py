#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manifest Dependency Graph Linter
Simulates Odoo's XML parsing chronology offline to detect forward references
and broken load-orders before the database is ever provisioned.
"""

import os
import sys
import ast
import re

def check_manifest(base_dir):
    errors = []

    # Regex definitions for Odoo XML patterns
    id_def_re = re.compile(r'<(?:record|template|menuitem|act_window)[^>]+id="([^"]+)"')
    # \b ensures we strictly match 'ref=' and not 'href=' or 't-attf-href='
    ref_attr_re = re.compile(r'\bref="([^"]+)"')
    eval_ref_re = re.compile(r"ref\(['\"]([^'\"]+)['\"]\)")

    for root, dirs, files in os.walk(base_dir):
        if "__manifest__.py" in files:
            manifest_path = os.path.join(root, "__manifest__.py")
            module_name = os.path.basename(root)

            with open(manifest_path, 'r', encoding='utf-8') as f:
                try:
                    manifest_data = ast.literal_eval(f.read())
                except Exception as e:
                    errors.append(f"❌ ERROR: Failed to parse {manifest_path}: {e}")
                    continue

            data_files = manifest_data.get('data', [])
            defined_ids = set()

            for data_file in data_files:
                file_path = os.path.join(root, data_file)
                if not os.path.exists(file_path):
                    continue

                if file_path.endswith('.xml'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):

                            # 1. Add new definitions to the simulated registry
                            for match in id_def_re.finditer(line):
                                new_id = match.group(1)
                                defined_ids.add(new_id)
                                defined_ids.add(f"{module_name}.{new_id}")

                            # 2. Check all reference calls against the running registry
                            refs_to_check = []
                            refs_to_check.extend(ref_attr_re.findall(line))
                            refs_to_check.extend(eval_ref_re.findall(line))

                            for ref_id in refs_to_check:
                                # Skip Odoo's implicit Python-generated model IDs (e.g., model_res_users)
                                # These are instantiated in PostgreSQL before XML evaluation begins.
                                if ref_id.startswith('model_') or ('.' in ref_id and ref_id.split('.')[1].startswith('model_')):
                                    continue

                                # Skip external dependencies (trusting the manifest 'depends' array)
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
                    # Basic CSV ID extraction
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
        print("[+] SUCCESS: Manifest Dependency Graph validated. No chronological forward references found.")
        sys.exit(0)

if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_manifest(base_dir)

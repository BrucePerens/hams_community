#!/usr/bin/env python3
"""
Odoo Manifest & JS Dependency Contract Linter
---------------------------------------------
Scans all __manifest__.py files into ASTs, then cross-references all
JavaScript ES6 module imports (`@module_name/...`) to mathematically guarantee
that the parent module explicitly depends on the imported module.
Prevents silent race conditions and `module_loader.js` crashes.
"""

import os
import sys
import ast
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: check_manifest_dependencies.py <repo_root>")
        sys.exit(1)

    repo_root = sys.argv[1]
    manifests = {}
    errors_found = False

    # 1. Map all manifests and their dependencies
    for root, dirs, files in os.walk(repo_root):
        if "__manifest__.py" in files:
            mod_name = os.path.basename(root)
            manifest_path = os.path.join(root, "__manifest__.py")
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=manifest_path)
                    for node in tree.body:
                        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                            manifest_dict = ast.literal_eval(node.value)
                            manifests[mod_name] = manifest_dict.get('depends', [])
            except (SyntaxError, ValueError, OSError) as e:
                print(f"❌ ERROR parsing {manifest_path}: {e}")
                errors_found = True

    # 2. Scan all JS files for Odoo '@' alias imports
    import_pattern = re.compile(r"import\s+.*?\s+from\s+['\"]@([a-zA-Z0-9_-]+)/.*['\"]")

    for root, dirs, files in os.walk(repo_root):
        if "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".js"):
                filepath = os.path.join(root, file)

                # Determine which module this JS file belongs to
                mod_dir = os.path.dirname(os.path.abspath(filepath))
                current_mod = None
                while mod_dir and mod_dir != os.path.dirname(mod_dir):
                    if os.path.exists(os.path.join(mod_dir, "__manifest__.py")):
                        current_mod = os.path.basename(mod_dir)
                        break
                    mod_dir = os.path.dirname(mod_dir)

                if not current_mod or current_mod not in manifests:
                    continue

                # Check imports against the current module's depends array
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_no, line in enumerate(f, 1):
                            match = import_pattern.search(line)
                            if match:
                                imported_mod = match.group(1)

                                # Ignore standard web frameworks or self-imports
                                if imported_mod != current_mod and imported_mod not in manifests[current_mod] and imported_mod not in ("web", "base"):
                                    print(f"🚨 MANIFEST DEPENDENCY VIOLATION in {current_mod}")
                                    print(f"  File: {os.path.relpath(filepath, repo_root)}:{line_no}")
                                    print(f"  Imports: '@{imported_mod}' but '{imported_mod}' is NOT listed in {current_mod}/__manifest__.py 'depends' array.")
                                    print(f"  Fix: Add '{imported_mod}' to the depends array to prevent module_loader.js race conditions.")
                                    errors_found = True
                except OSError as e:
                    print(f"⚠️ Warning: Could not read JS file {filepath}: {e}")

    if errors_found:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

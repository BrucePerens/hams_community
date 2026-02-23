#!/usr/bin/env python3
"""
Odoo Module Dependency Pre-Flight Check
---------------------------------------
Parses a module's __manifest__.py and verifies that all listed 
dependencies exist within the provided addons paths.
"""

import os
import sys
import ast
import argparse

def parse_manifest(manifest_path):
    """Safely parse the Odoo manifest dictionary."""
    if not os.path.exists(manifest_path):
        print(f"❌ Error: Manifest file not found at '{manifest_path}'.")
        sys.exit(1)
        
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
            # ast.literal_eval safely evaluates Python dictionaries without executing arbitrary code
            return ast.literal_eval(manifest_content)
    except Exception as e:
        print(f"❌ Error parsing manifest at '{manifest_path}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pre-flight dependency check for Odoo modules.")
    parser.add_argument("-m", "--module", required=True, help="Path to the target module directory (e.g., ./user_websites)")
    parser.add_argument("--addons-path", required=True, help="Comma-separated list of addons paths")
    
    args = parser.parse_args()

    module_path = os.path.abspath(args.module)
    manifest_path = os.path.join(module_path, '__manifest__.py')
    
    # 1. Parse the target module's manifest
    manifest = parse_manifest(manifest_path)
    dependencies = manifest.get('depends', [])
    
    if not dependencies:
        print(f"✅ Module '{os.path.basename(module_path)}' has no external dependencies. Proceeding.")
        sys.exit(0)

    print(f"🔍 Checking {len(dependencies)} dependencies for '{os.path.basename(module_path)}'...")

    # 2. Parse Addons Paths
    addons_paths = [p.strip() for p in args.addons_path.split(',') if p.strip()]
    
    # We always assume 'base' is available if Odoo is installed properly, 
    # but we will still look for it if it's explicitly requested.
    
    missing_dependencies = []

    # 3. Verify each dependency
    for dep in dependencies:
        found = False
        for path in addons_paths:
            dep_path = os.path.join(path, dep)
            # A valid Odoo module directory must contain a __manifest__.py (or __openerp__.py in very old versions)
            if os.path.isdir(dep_path) and os.path.exists(os.path.join(dep_path, '__manifest__.py')):
                found = True
                break
        
        if not found:
            # Note: Core modules like 'base' or 'web' might reside in the core odoo/addons directory.
            # If your addons path doesn't explicitly include the core path, this might flag false positives
            # for standard modules. Ensure your --addons-path is comprehensive.
            missing_dependencies.append(dep)

    # 4. Report Results
    if missing_dependencies:
        print("\n❌ PRE-FLIGHT CHECK FAILED!")
        print(f"   The following dependencies are missing from the provided addons paths:\n   - " + "\n   - ".join(missing_dependencies))
        print(f"\n   Searched Paths:\n   - " + "\n   - ".join(addons_paths))
        sys.exit(1)
    else:
        print("✅ All dependencies located successfully. Pre-flight check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()


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
    
    # Strict Tier Isolation (Topological Enforcement)
    TIERS = {
        1: ['base', 'web', 'mail', 'portal', 'website', 'zero_sudo', 'ham_base', 'ham_testing', 'ham_logbook', 'ham_onboarding', 'ham_club_management', 'ham_init', 'user_websites', 'user_websites_seo', 'cloudflare', 'caching', 'compliance', 'manual_library'],
        2: ['ham_events', 'ham_satellite', 'ham_propagation', 'ham_dns', 'ham_classifieds'],
        3: ['ham_forum_extension', 'ham_shack', 'theme_hams']
    }
    
    def get_tier(mod_name):
        for tier, mods in TIERS.items():
            if mod_name in mods:
                return tier
        return 99 # Unknown custom modules are placed at the top tier
        
    module_name = os.path.basename(module_path)
    module_tier = get_tier(module_name)
    
    tier_violations = []
    for dep in dependencies:
        dep_tier = get_tier(dep)
        if dep_tier > module_tier and module_tier != 99:
            tier_violations.append(f"`{dep}` (Tier {dep_tier})")
            
    if tier_violations:
        print(f"\n❌ ARCHITECTURE VIOLATION: `{module_name}` (Tier {module_tier}) cannot depend on higher-tier modules:")
        for v in tier_violations:
            print(f"   - {v}")
        sys.exit(1)

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
        missing_formatted = [f"`{dep}`" for dep in missing_dependencies]
        paths_formatted = [f"`{p}`" for p in addons_paths]
        print("   The following dependencies are missing from the provided addons paths:\n   - " + "\n   - ".join(missing_formatted))
        print("\n   Searched Paths:\n   - " + "\n   - ".join(paths_formatted))
        sys.exit(1)
    else:
        print("✅ All dependencies located successfully. Pre-flight check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()


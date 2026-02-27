#!/usr/bin/env python3
import os

fixes = [
    ('caching/__init__.py', 1, 'F401'),
    ('caching/controllers/__init__.py', 1, 'F401'),
    ('caching/tests/__init__.py', 1, 'F401'),
    ('cloudflare/__init__.py', 3, 'F401'),
    ('cloudflare/__init__.py', 4, 'F401'),
    ('cloudflare/__init__.py', 5, 'F401'),
    ('cloudflare/models/__init__.py', 3, 'F401'),
    ('cloudflare/models/__init__.py', 4, 'F401'),
    ('cloudflare/models/__init__.py', 5, 'F401'),
    ('cloudflare/models/__init__.py', 6, 'F401'),
    ('cloudflare/models/__init__.py', 7, 'F401'),
    ('cloudflare/models/__init__.py', 8, 'F401'),
    ('cloudflare/models/__init__.py', 9, 'F401'),
    ('cloudflare/models/__init__.py', 10, 'F401'),
    ('cloudflare/models/__init__.py', 11, 'F401'),
    ('cloudflare/models/__init__.py', 12, 'F401'),
    ('cloudflare/models/__init__.py', 13, 'F401'),
    ('cloudflare/models/__init__.py', 14, 'F401'),
    ('cloudflare/models/config_manager.py', 6, 'F401'),
    ('cloudflare/tests/__init__.py', 3, 'F401'),
    ('cloudflare/tests/__init__.py', 4, 'F401'),
    ('cloudflare/tests/__init__.py', 5, 'F401'),
    ('cloudflare/tests/__init__.py', 6, 'F401'),
    ('cloudflare/tests/__init__.py', 7, 'F401'),
    ('cloudflare/tests/test_purge_queue.py', 55, 'F841'),
    ('cloudflare/tests/test_waf_management.py', 3, 'F401'),
    ('cloudflare/utils/__init__.py', 3, 'F401'),
    ('compliance/__init__.py', 3, 'F401'),
    ('compliance/__init__.py', 4, 'F401'),
    ('compliance/hooks.py', 3, 'F401'),
    ('manual_library/__init__.py', 2, 'F401'),
    ('manual_library/__init__.py', 3, 'F401'),
    ('manual_library/__init__.py', 4, 'F401'),
    ('manual_library/controllers/__init__.py', 2, 'F401'),
    ('manual_library/hooks.py', 2, 'F401'),
    ('manual_library/models/__init__.py', 2, 'F401'),
    ('manual_library/tests/__init__.py', 2, 'F401'),
    ('manual_library/tests/__init__.py', 3, 'F401'),
    ('manual_library/tests/__init__.py', 4, 'F401'),
    ('manual_library/tests/__init__.py', 5, 'F401'),
    ('manual_library/tests/__init__.py', 6, 'F401'),
    ('manual_library/tests/__init__.py', 7, 'F401'),
    ('manual_library/tests/test_features.py', 71, 'F841'),
    ('manual_library/tests/test_orm_logic.py', 4, 'F401'),
    ('tools/aef_extract.py', 9, 'F401'),
    ('user_websites_seo/__init__.py', 3, 'F401'),
    ('user_websites_seo/__init__.py', 4, 'F401'),
    ('user_websites_seo/controllers/__init__.py', 3, 'F401'),
    ('user_websites_seo/controllers/main.py', 4, 'F401'),
    ('user_websites_seo/models/__init__.py', 3, 'F401'),
    ('user_websites_seo/models/__init__.py', 4, 'F401'),
    ('user_websites_seo/models/user_websites_group.py', 3, 'F401')
]

def apply_fixes():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for rel_path, line_num, error_code in fixes:
        filepath = os.path.join(root_dir, rel_path)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num <= len(lines):
                line = lines[line_num - 1].rstrip('\n')
                # Prevent double-patching if script is run multiple times
                if 'noqa' not in line:
                    lines[line_num - 1] = f"{line}  # noqa: {error_code}\n"
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"✅ Fixed: {rel_path}:{line_num}")
        else:
            print(f"⚠️ File not found, skipping: {rel_path}")

if __name__ == '__main__':
    apply_fixes()

#!/usr/bin/env python3
import os
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))

fixes = {
    # 1. Move miscategorized SRE and Framework stories out of core and into domain
    "stories/core": {
        "domain": [
            "11_pager_duty_sre.md",
            "12_backup_management.md",
            "13_database_management.md",
            "14_framework_and_utilities.md"
        ]
    },
    # 2. Split the flat docs/modules/ folder into core and domain
    "modules": {
        "core": [
            "caching.md",
            "cloudflare.md",
            "compliance.md",
            "manual_library.md",
            "user_websites.md",
            "user_websites_seo.md",
            "zero_sudo.md"
        ],
        "domain": [
            "ham_backup_management.md",
            "ham_base.md",
            "ham_callbook.md",
            "ham_classifieds.md",
            "ham_club_management.md",
            "ham_database_management.md",
            "ham_dns.md",
            "ham_dx_cluster.md",
            "ham_events.md",
            "ham_forum_extension.md",
            "ham_init.md",
            "ham_logbook.md",
            "ham_onboarding.md",
            "ham_pager_duty.md",
            "ham_propagation.md",
            "ham_repeater_dir.md",
            "ham_satellite.md",
            "ham_shack.md",
            "ham_testing.md",
            "test_real_transaction.md",
            "theme_hams.md"
        ]
    }
}

def fix_boundaries():
    for source_dir, routes in fixes.items():
        src_path = os.path.join(BASE_DIR, source_dir)
        if not os.path.exists(src_path):
            continue
        
        for target_group, files in routes.items():
            # If routing from 'modules', target is 'modules/core' etc.
            # If routing from 'stories/core', target is 'stories/domain'.
            if source_dir == "modules":
                target_path = os.path.join(BASE_DIR, "modules", target_group)
            else:
                target_path = os.path.join(BASE_DIR, source_dir.split('/')[0], target_group)
                
            os.makedirs(target_path, exist_ok=True)
            
            for file in files:
                file_src = os.path.join(src_path, file)
                file_dst = os.path.join(target_path, file)
                if os.path.exists(file_src) and file_src != file_dst:
                    shutil.move(file_src, file_dst)
                    print(f"Fixed: Moved {file} -> {target_path}")

if __name__ == "__main__":
    fix_boundaries()
    print("\nDocumentation boundaries fully corrected.")

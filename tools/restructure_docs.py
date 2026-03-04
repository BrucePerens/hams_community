#!/usr/bin/env python3
import os
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))

moves = {
    "adrs": {
        "core": [
            "MASTER_01_SECURITY_ZERO_SUDO.md",
            "MASTER_03_EDGE_ROUTING_THREAT_MITIGATION.md",
            "MASTER_04_MODULARITY_SHARED_SERVICES.md",
            "MASTER_08_CORE_ARCHITECTURE_PERFORMANCE.md",
            "MASTER_10_IDENTITY_ACCESS_CONTROL.md",
            "MASTER_11_DEVELOPMENT_WORKFLOW_DOCS.md",
            "MASTER_12_QA_TESTING_MANDATES.md",
            "MASTER_14_LLM_CONTEXT_MANAGEMENT.md",
            "0060_strict_syntactic_parsing_mandate.md",
            "0061_real_transaction_testing_facility.md",
            "0062_micro_service_account_pattern.md",
            "0063_linter_anti_evasion_protocols.md",
            "0064_micro_service_strict_acl_isolation.md",
            "0065_headless_api_translation_ban.md"
        ],
        "domain": [
            "MASTER_02_DATA_PRIVACY_RETENTION.md",
            "MASTER_05_SWL_LIFECYCLE.md",
            "MASTER_06_DNS_CQRS.md",
            "MASTER_07_ZERO_DB_ARCHITECTURE.md",
            "MASTER_09_API_INTEGRATIONS.md",
            "MASTER_13_FRONTEND_UX.md",
            "MASTER_15_DOMAIN_IDENTITY.md",
            "0064_shadow_profile_pattern.md"
        ]
    },
    "runbooks": {
        "core": [
            "01_deployment_and_provisioning.md",
            "04_security_and_compliance.md",
            "06_ci_cd_pipeline.md",
            "07_caching_infrastructure.md",
            "cloudflare_operations.md"
        ],
        "domain": [
            "02_daemon_management.md",
            "03_disaster_recovery.md",
            "05_api_and_webhooks.md"
        ]
    },
    "stories": {
        "core": [
            "11_pager_duty_sre.md",
            "12_backup_management.md",
            "13_database_management.md",
            "14_framework_and_utilities.md",
            "cloudflare_edge.md"
        ],
        "domain": [
            "01_identity_and_onboarding.md",
            "02_logbook_and_awards.md",
            "03_dx_cluster_and_shack.md",
            "04_callbook_and_privacy.md",
            "05_events_and_clubs.md",
            "06_infrastructure_and_market.md",
            "07_satellite_and_repeaters.md",
            "08_elmering_forums.md",
            "09_propagation_maps.md",
            "10_testing_and_education.md"
        ]
    },
    "journeys": {
        "core": [
            "04_personal_website_and_dns.md",
            "cloudflare_admin_journey.md"
        ],
        "domain": [
            "01_onboarding_and_identity.md",
            "02_live_qso_logging.md",
            "03_club_governance.md",
            "05_swl_onboarding_and_upgrade.md"
        ]
    },
    "security_models": {
        "core": [],
        "domain": [
            "01_onboarding_and_api_threat_model.md",
            "02_propagation_threat_model.md"
        ]
    }
}

def restructure():
    for category, groups in moves.items():
        cat_dir = os.path.join(BASE_DIR, category)
        if not os.path.exists(cat_dir):
            continue
        for group, files in groups.items():
            target_dir = os.path.join(cat_dir, group)
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                src = os.path.join(cat_dir, file)
                dst = os.path.join(target_dir, file)
                if os.path.exists(src) and src != dst:
                    shutil.move(src, dst)
                    print(f"Moved {file} -> {category}/{group}/")

if __name__ == "__main__":
    restructure()
    print("Documentation successfully restructured into core/ and domain/ boundaries.")

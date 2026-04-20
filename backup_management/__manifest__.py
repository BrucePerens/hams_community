# -*- coding: utf-8 -*-
{
    "name": "Backup Management",
    "summary": "Unified Backup Management Facility (Kopia & pgBackRest)",
    "author": "Bruce Perens K6BP",
    "category": "Ham Radio",
    "license": "AGPL-3",
    "version": "1.0",
    "depends": ["base", "mail", "zero_sudo", "test_real_transaction", "binary_downloader"],
    "external_dependencies": {
        "python": ["pika", "cryptography"],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/backup_config_views.xml",
        "views/restore_wizard_views.xml",
        "views/backup_snapshot_views.xml",
        "views/backup_job_views.xml",

        "views/backup_board_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "backup_management/static/src/components/board/board.js",
            "backup_management/static/src/components/board/board.xml",
        ]
    },
}

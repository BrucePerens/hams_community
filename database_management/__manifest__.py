# -*- coding: utf-8 -*-
{
    "name": "Database Management",
    "summary": "DBA Toolkit for Autovacuum, Dead Tuples, and Slow Queries",
    "author": "Bruce Perens K6BP",
    "category": "Ham Radio",
    "license": "AGPL-3",
    "version": "1.0",
    "depends": ["base", "mail", "zero_sudo", "binary_downloader", "manual_library"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/db_stats_views.xml",
        "views/pg_config_views.xml",
        "views/menu_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}

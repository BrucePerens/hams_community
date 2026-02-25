#!/usr/bin/env python3
# -*- coding: utf-8 -*-
{
    "name": "Cloudflare Edge Orchestration",
    "summary": "Generalized CDN Edge Orchestration, Proactive Purging, and WAF Management.",
    "author": "Open Source Community",
    "category": "Website",
    "version": "1.1",
    "license": "AGPL-3",
    "depends": ["base", "web", "zero_sudo"],
    "data": [
        "security/security_data.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/res_config_settings_views.xml",
        "views/cloudflare_menus.xml",
        "views/ip_ban_views.xml",
        "views/waf_rule_views.xml",
        "views/config_backup_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}

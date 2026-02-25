#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
{
    'name': 'Ham Radio Cloudflare Edge',
    'summary': 'CDN Edge Orchestration, Proactive Purging, and WAF Management.',
    'author': 'Bruce Perens K6BP',
    'category': 'Ham Radio/Infrastructure',
    'version': '1.0',
    'license': 'Proprietary',
    'depends': ['base', 'website', 'website_blog', 'website_sale', 'ham_base', 'user_websites', 'ham_classifieds'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/res_config_settings_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
}

# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
{
    'name': "Global Compliance & Privacy",
    'summary': "Automated configuration of GDPR/CCPA settings and legal pages.",
    'description': """
This module acts as a central hub for regulatory compliance across the project. 
Upon installation, it:
- Automatically enables Odoo's native Cookie Consent Bar.
- Provisions standard editable legal pages (Privacy Policy, Cookie Policy, Terms of Service) via noupdate XML, ensuring site owner edits are never overwritten.
    """,
    'author': "Bruce Perens K6BP",
    'website': "https://perens.com/",
    'category': 'Website',
    'version': '1.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',
        'portal',
    ],
    'data': [
        'data/legal_pages_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}

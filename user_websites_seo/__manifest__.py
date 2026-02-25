# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
{
    'name': "User Websites SEO",
    'summary': "Lets users optimize their personal and group blogs for search engines.",
    'description': "Inherits website.seo.metadata onto user profiles to restore the QWeb SEO widget.",
    'author': "Bruce Perens K6BP",
    'website': "https://perens.com/",
    'category': 'Website',
    'version': '1.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',
        'user_websites',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': True,
}

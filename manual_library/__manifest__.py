# -*- coding: utf-8 -*-
{
    'name': "Manual Library",
    'summary': "Hierarchical documentation and knowledge-base system",
    'description': """
A clean-room, open-source implementation of a hierarchical documentation 
system for Odoo Community. Provides API interoperability for the 
knowledge.article model. Includes frontend search, feedback, and dynamic TOC.
    """,
    'author': "Community",
    'website': "https://example.com",
    'category': 'Website',
    'version': '1.1',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'website',
    ],
    'data': [
        'security/manual_library_security.xml',
        'security/ir.model.access.csv',
        'views/knowledge_article_views.xml',
        'views/knowledge_article_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'manual_library/static/src/js/manual_toc.js',
        ],
        'web.assets_tests': [
            'manual_library/static/tests/tours/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}

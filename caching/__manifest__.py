{
    'name': 'Caching PWA',
    'version': '1.0',
    'author': 'Bruce Perens K6BP',
    'category': 'Website',
    'summary': 'Global Service Worker for aggressive frontend asset caching',
    'description': 'Intercepts network requests to cache Odoo JS/CSS bundles and static files on the client edge. Zero-config integration for other modules.',
    'depends': ['base', 'website'],
    'data': [
        'views/layout_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

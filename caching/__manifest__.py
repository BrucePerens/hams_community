{
    "name": "Caching PWA",
    "version": "1.0",
    "author": "Bruce Perens K6BP",
    "category": "Website",
    "summary": "Global Service Worker for aggressive caching",
    "description": (
        "Intercepts network requests to cache Odoo JS/CSS bundles "
        "and static files on the client edge. Zero-config."
    ),
    "depends": [
        "base",
        "website",
        "zero_sudo",
        "hams_test",
        "manual_library",
    ],
    "data": [
        "data/security_data.xml",
        "security/ir.model.access.csv",
        "views/layout_inherit.xml",
        "views/res_config_settings_views.xml",
    ],
    "knowledge_docs": [
        {
            "name": "Caching Module Documentation",
            "path": "data/documentation.html",
            "icon": "⚡",
            "category": "workspace",
        }
    ],
    "assets": {
        "web.assets_tests": [
            "caching/static/tests/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

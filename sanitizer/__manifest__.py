{
    "name": "Ham Sanitizer Override",
    "summary": "Authorizes <script> and <iframe> tags globally within the Odoo HTML sanitizer.",
    "version": "1.0.0",
    "author": "Bruce Perens K6BP",
    "license": "Other proprietary",
    "category": "Core",
    "depends": ["base", "mail"],
    "installable": True,
    "application": False,
    "auto_install": True,
    "post_load": "post_load",
    "knowledge_docs": [
        {
            "name": "Ham Sanitizer Override Documentation",
            "path": "data/documentation.html",
            "icon": "🛡️",
            "category": "workspace",
        }
    ],
}

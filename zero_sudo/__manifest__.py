{
    "name": "Zero-Sudo Security Core",
    "summary": "Foundational security utilities, service account patterns, and web isolation.",
    "author": "Bruce Perens K6BP",
    "category": "Security",
    "version": "1.0",
    "license": "AGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "data/security_data.xml",
        "security/ir.model.access.csv",
        "views/res_users_views.xml"
    ],
    "installable": True,
    "auto_install": False,
}

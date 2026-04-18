{
    "name": "Distributed Redis Cache",
    "summary": "Fine-grained distributed caching and phase coherence for horizontally scaled Odoo clusters.",
    "description": """
Distributed Redis Cache
=======================
* Fine-grained distributed caching and phase-coherence for horizontally-scaled Odoo clusters.
* Invalidates a single cached database when necessary, rather than all of them together (as Odoo's cache would do), providing a significant speed optimization.
* Replaces Odoo's internal cache.
    """,
    "author": "Bruce Perens K6BP",
    "website": "[https://perens.com/](https://perens.com/)",
    "category": "Technical",
    "version": "1.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "installable": True,
    "application": False,
    "auto_install": False,
}

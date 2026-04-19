{
    "name": "Distributed Redis Cache",
    "summary": "Fine-grained distributed caching and phase coherence for horizontally scaled Odoo clusters.",
    "description": """
Distributed Redis Cache
=======================
* Fine-grained distributed caching and phase-coherence for horizontally-scaled Odoo clusters.
* Invalidates a single cached database when necessary, rather than all of them together (as Odoo's cache would do), providing a significant speed optimization.
* Replaces Odoo's internal cache.
* Includes a UI to manage the cache and check Redis status.
    """,
    "author": "Bruce Perens K6BP",
    "website": "https://perens.com/",
    "category": "Technical",
    "version": "1.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "views/distributed_cache_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

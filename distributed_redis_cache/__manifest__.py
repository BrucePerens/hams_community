#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. AGPL-3.0.
{
    "name": "Distributed Redis Cache",
    "description": """
       Distributed Redis Cache
       =======================
       * Fine-grained distributed caching and phase-coherence for horizontally-scaled Odoo clusters.
       * Invalidates a single cached database when necessary, rather than all of them together (as Odoo's cache would do), providing a significant speed optimization.
       * Replaces Odoo's internal cache.
    """,
    "summary": "Fine-grained distributed caching and phase coherence for horizontally scaled Odoo clusters.",
    "author": "Bruce Perens K6BP",
    "website": "https://perens.com/",
    "category": "Technical",
    "version": "1.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "installable": True,
    "application": False,
    "auto_install": False,
}

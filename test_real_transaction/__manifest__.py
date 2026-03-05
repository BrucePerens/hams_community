#!/usr/bin/env python3
# -*- coding: utf-8 -*-
{
    'name': 'Real Transaction Testing Facility',
    'version': '1.0',
    'author': 'Bruce Perens K6BP',
    'category': 'Technical Settings',
    'summary': 'Developer tool for testing Odoo with real database commits.',
    'description': """
        Provides a RealTransactionCase class that bypasses Odoo's test cursor wrapping.
        This allows developers to write tests that perform true database commits, 
        which is critical for testing One2many inverse cache anomalies and cross-worker behaviors.
    """,
    'depends': ['base'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

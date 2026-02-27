# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import api, SUPERUSER_ID  # noqa: F401
from odoo.tools import file_open

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if 'knowledge.article' in env:
        article_model = env['knowledge.article']
        existing = article_model.search([('name', '=', 'Site Owner\'s Guide to Regulatory Compliance')], limit=1)
        
        if not existing:
            # Read the HTML content securely using Odoo's file_open utility
            try:
                with file_open('compliance/data/documentation.html', 'r') as f:
                    doc_body = f.read()
            except Exception as e:
                # Failsafe if the file is missing or unreadable
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                'name': 'Site Owner\'s Guide to Regulatory Compliance',
                'body': doc_body,
            }
            # Dynamically check for fields to ensure broad API compatibility
            if 'is_published' in article_model._fields:
                vals['is_published'] = True
            if 'category' in article_model._fields:
                vals['category'] = 'workspace'
            if 'internal_permission' in article_model._fields:
                vals['internal_permission'] = 'read'
            if 'icon' in article_model._fields:
                vals['icon'] = '⚖️'
                
            return article_model.create(vals)
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation.
    1. Enforces the use of Odoo's native cookie consent banner.
    2. Installs the regulatory documentation via the Knowledge API.
    """
    websites = env['website'].search([], limit=10000)
    
    # Safely check if the target field exists in the current Odoo version
    if 'cookies_bar' in env['website']._fields:
        websites.write({'cookies_bar': True})
        
    # Install documentation
    install_knowledge_docs(env)

# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID  # noqa: F401
from odoo.tools import file_open

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if 'knowledge.article' in env:
        article_model = env['knowledge.article']
        existing = article_model.search([('name', '=', 'Manual Library Documentation')], limit=1)
        
        if not existing:
            try:
                with file_open('manual_library/data/documentation.html', 'r') as f:
                    doc_body = f.read()
            except Exception as e:
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                'name': 'Manual Library Documentation',
                'body': doc_body,
            }
            # Dynamically check for fields to ensure broad API compatibility
            if 'is_published' in article_model._fields:
                vals['is_published'] = True
            if 'internal_permission' in article_model._fields:
                vals['internal_permission'] = 'read'
            if 'icon' in article_model._fields:
                vals['icon'] = '📚'
                
            return article_model.create(vals)
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation. 
    Injects docs into the knowledge base.
    """
    install_knowledge_docs(env)

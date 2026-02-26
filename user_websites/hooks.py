# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.tools import file_open

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if 'knowledge.article' in env:
        article_model = env['knowledge.article']
        existing = article_model.search([('name', '=', 'User Websites Documentation')], limit=1)
        
        if not existing:
            try:
                with file_open('user_websites/data/documentation.html', 'r') as f:
                    doc_body = f.read()
            except Exception as e:
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                'name': 'User Websites Documentation',
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
                vals['icon'] = '🌐'
                
            return article_model.create(vals)
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation. 
    Injects docs into the knowledge base if the API is already installed.
    """
    install_knowledge_docs(env)

    # Create partial indexes for highly-queried boolean states to optimize read performance
    env.cr.execute("CREATE INDEX IF NOT EXISTS idx_website_page_published ON website_page (id) WHERE website_published = TRUE;")
    env.cr.execute("CREATE INDEX IF NOT EXISTS idx_blog_post_published ON blog_post (id) WHERE is_published = TRUE;")

    # Soft-Dependency: Retroactively lock down the Cloudflare service account if it was installed first
    cf_svc = env.ref('cloudflare.user_cloudflare_service', raise_if_not_found=False)
    if cf_svc and 'is_service_account' in cf_svc._fields:
        cf_svc.write({'is_service_account': True})

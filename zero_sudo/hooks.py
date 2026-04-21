# -*- coding: utf-8 -*-

def post_init_hook(env):
    """
    Hook executed upon module installation.
    Injects docs into the knowledge base using the centralized declarative facility.
    """
    if 'ir.module.module' in env:
        env['ir.module.module']._bootstrap_knowledge_docs()

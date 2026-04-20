# -*- coding: utf-8 -*-
import os # noqa: F401
from odoo import api, SUPERUSER_ID, _ # noqa: F401
from odoo.tools import misc # noqa: F401

def post_init_hook(env):
    """
    Installs the module's LLM documentation into the Manual Library.
    Refactored to follow ADR-0001 least-privilege principles by escalating through a service account.
    """
    svc_uid = env['zero_sudo.security.utils']._get_service_uid('daemon_key_manager.user_daemon_key_manager_service')
    with_svc_env = env.user.with_user(svc_uid).with_context(mail_notrack=True, prefetch_fields=False).env

    doc_path = misc.file_path('daemon_key_manager/LLM_DOCUMENTATION.md')
    if os.path.exists(doc_path):
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        with_svc_env['knowledge.article'].create({
            'name': 'Daemon Key Manager Documentation',
            'body': content,
            'is_published': True,
        })

# -*- coding: utf-8 -*-
from odoo.tools import file_open, _
import logging

_logger = logging.getLogger(__name__)

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if "knowledge.article" in env:
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "manual_library.user_manual_library_service_account"
        )
        article_model = env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Real Transaction Testing Facility Guide")], limit=1
        )

        if not existing:
            try:
                with file_open("test_real_transaction/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                _logger.error(_("Failed to load real transaction documentation file: %s"), e)
                doc_body = _("<p>Error loading documentation file: %s</p>") % e

            vals = {
                "name": "Real Transaction Testing Facility Guide",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "category" in article_model._fields:
                vals["category"] = "workspace"
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🧪"

            return article_model.create(vals)
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation.
    Installs the documentation via the Knowledge API.
    """
    install_knowledge_docs(env)

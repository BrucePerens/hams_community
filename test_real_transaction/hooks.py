# -*- coding: utf-8 -*-
from odoo.tools import file_open, _
import logging

_logger = logging.getLogger(__name__)

def install_knowledge_docs(env):
    # [@ANCHOR: documentation_injection]
    article_model_name = None
    if "knowledge.article" in env:
        article_model_name = "knowledge.article"
    elif "manual.article" in env:
        article_model_name = "manual.article"

    if article_model_name:
        # Use our own dedicated service account first,
        # fallback to manual_library or general facility if needed.
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "test_real_transaction.user_real_transaction_service"
        )
        if not svc_uid:
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "manual_library.user_manual_library_service_account"
            )
        if not svc_uid:
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "zero_sudo.odoo_facility_service_internal"
            )

        if not svc_uid:
            _logger.warning(_("Could not find a suitable service account for documentation installation."))
            return None

        article_model = env[article_model_name].with_user(svc_uid).with_context(
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
    pass

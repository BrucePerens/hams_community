# -*- coding: utf-8 -*-
import logging
from odoo import _
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

def install_knowledge_docs(env):
    # [@ANCHOR: binary_doc_bootstrap]
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    This handles both manual_library and the Odoo Enterprise knowledge module.
    """
    if "knowledge.article" in env:
        # Prefer the manual_library service account if available,
        # otherwise fallback to the general facility service account.
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "manual_library.user_manual_library_service_account"
        )
        if not svc_uid:
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "zero_sudo.odoo_facility_service_internal"
            )

        if not svc_uid:
            _logger.warning("Could not find a suitable service account for documentation installation.")
            return None

        article_model = env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Binary Downloader Facility")], limit=1
        )

        if not existing:
            try:
                with file_open("binary_downloader/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                _logger.error("Failed to load documentation file: %s", e)
                doc_body = _("<p>Error loading documentation file: %s</p>") % e

            vals = {
                "name": "Binary Downloader Facility",
                "body": doc_body,
            }
            # Dynamically check for fields to ensure broad API compatibility
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "📦"

            return article_model.create(vals)
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation.
    """
    pass

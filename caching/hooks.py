# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import api, SUPERUSER_ID  # noqa: F401
from odoo.tools import file_open
import logging

_logger = logging.getLogger(__name__)

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    Supports both 'knowledge' (Enterprise) and 'manual_library' (Community)
    by checking for the model existence.
    """
    if "knowledge.article" in env:
        # Check if already installed to avoid redundant work
        # We use a system parameter to track installation to avoid searching every time if it's missing
        utils = env["zero_sudo.security.utils"]

        # We try to get the service account for documentation.
        # In this repo, manual_library.user_manual_library_service_account is the standard.
        # If it doesn't exist (e.g. only 'knowledge' is installed), we fallback to odoo_facility_service_internal.

        svc_account = "manual_library.user_manual_library_service_account"
        if not env["ir.model.data"]._xmlid_to_res_id(svc_account, raise_if_not_found=False):
             svc_account = "zero_sudo.odoo_facility_service_internal"

        svc_uid = utils._get_service_uid(svc_account)
        _logger.info("Installing caching documentation using service account: %s (UID: %s)", svc_account, svc_uid)

        article_model = env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Caching Module Documentation")], limit=1
        )

        if not existing:
            # Read the HTML content securely using Odoo's file_open utility
            try:
                with file_open("caching/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                _logger.error("Failed to load caching documentation file: %s", e)
                # Failsafe if the file is missing or unreadable
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Caching Module Documentation",
                "body": doc_body,
            }
            # Dynamically check for fields to ensure broad API compatibility
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "category" in article_model._fields:
                vals["category"] = "workspace"
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "⚡"

            return article_model.create(vals)
        return existing
    return None


def post_init_hook(env):
    """
    Hook executed upon module installation.
    Installs the caching documentation via the Knowledge API.
    """
    install_knowledge_docs(env)

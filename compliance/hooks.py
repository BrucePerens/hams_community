# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import api, SUPERUSER_ID  # noqa: F401
from odoo.tools import file_open
import logging


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article or manual.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    # ADR-0055: Support soft dependencies on manual_library or enterprise knowledge.
    article_model_name = None
    if "knowledge.article" in env:
        article_model_name = "knowledge.article"
    elif "manual.article" in env:
        article_model_name = "manual.article"

    if article_model_name:
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "compliance.user_compliance_service"
        )
        # ADR-0002/0055: We typically use service accounts, but since we have a soft
        # dependency on an external model (knowledge/manual), we cannot define a
        # permanent ACL in ir.model.access.csv.
        # To bypass this for documentation injection only, we use .sudo().
        article_model = env[article_model_name].sudo().with_context(  # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Site Owner's Guide to Regulatory Compliance")], limit=1
        )

        if not existing:
            # Read the HTML content securely using Odoo's file_open utility
            try:
                with file_open("compliance/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                logging.getLogger(__name__).error("Failed to load compliance documentation file: %s", e)
                # Failsafe if the file is missing or unreadable
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Site Owner's Guide to Regulatory Compliance",
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
                vals["icon"] = "⚖️"

            try:
                return article_model.create(vals)
            except Exception as e:
                logging.getLogger(__name__).error("Failed to create compliance documentation article: %s", e)
        return existing
    return None


def post_init_hook(env):
    """
    Hook executed upon module installation.
    1. Enforces the use of Odoo's native cookie consent banner.
    2. Installs the regulatory documentation via the Knowledge API.
    """
    # ADR-0002: Zero-Sudo Architecture. We must not use .sudo() or stay as SUPERUSER.
    # We switch to a dedicated micro-privilege service account.
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid("compliance.user_compliance_service")

    websites = env["website"].with_user(svc_uid).search([], limit=10000)

    # Safely check if the target field exists in the current Odoo version
    if "cookies_bar" in env["website"]._fields:
        websites.write({"cookies_bar": True})

    # Install documentation
    install_knowledge_docs(env)

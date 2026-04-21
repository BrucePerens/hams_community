# -*- coding: utf-8 -*-
from odoo.tools import file_open


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if "knowledge.article" in env:
        # Use the internal facility service account to create the documentation
        # This follows the least-privilege principle for installing documentation.
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
        article_model = env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Zero-Sudo Security Core")], limit=1
        )

        if not existing:
            try:
                with file_open("zero_sudo/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Zero-Sudo Security Core",
                "body": doc_body,
            }
            # Dynamically check for fields to ensure broad API compatibility
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🛡️"

            return article_model.create(vals)
        return existing
    return None


def post_init_hook(env):
    """
    Hook executed upon module installation.
    Injects docs into the knowledge base.
    """
    install_knowledge_docs(env)

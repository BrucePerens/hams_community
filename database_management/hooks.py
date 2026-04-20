# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.tools import file_open


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if "knowledge.article" in env:
        # Use the specialized service account for Database Management to install documentation
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "database_management.user_database_management_service"
        )
        article_model = (
            env["knowledge.article"]
            .with_user(svc_uid)
            .with_context(mail_notrack=True, prefetch_fields=False)
        )

        existing = article_model.search(
            [("name", "=", "Database Management Guide")], limit=1
        )

        if not existing:
            try:
                with file_open("database_management/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                doc_body = f"<h1>Database Management Guide</h1><p>Welcome to the Database Management module.</p><p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Database Management Guide",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🛢"

            return article_model.create(vals)
        return existing
    return None


def post_init_hook(env):
    """
    Automatically install module documentation using the dedicated service account.
    """
    install_knowledge_docs(env)

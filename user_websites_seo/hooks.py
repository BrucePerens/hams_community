# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo.tools import file_open
import logging

def install_knowledge_docs(env):
    # [@ANCHOR: soft_dependency_docs_installation]
    # Verified by [@ANCHOR: test_soft_dependency_docs_installation]
    # Tests [@ANCHOR: soft_dependency_docs_installation]
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    article_model_name = None
    if "knowledge.article" in env:
        article_model_name = "knowledge.article"
    elif "manual.article" in env:
        article_model_name = "manual.article"

    if article_model_name:
        utils = env["zero_sudo.security.utils"]
        if env["ir.config_parameter"].sudo().get_param("user_websites_seo.docs_installed"): # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
            return None

        svc_uid = utils._get_service_uid("zero_sudo.facility_service_internal")
        article_model = env[article_model_name].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "User Websites SEO Guide")], limit=1
        )

        if not existing:
            try:
                with file_open("user_websites_seo/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                logging.getLogger(__name__).error("Failed to load SEO documentation file: %s", e)
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "User Websites SEO Guide",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "category" in article_model._fields:
                vals["category"] = "workspace"
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🔍"

            res = article_model.create(vals)
            if res:
                env["ir.config_parameter"].with_user(svc_uid).set_param("user_websites_seo.docs_installed", "1")
            return res
        else:
            env["ir.config_parameter"].with_user(svc_uid).set_param("user_websites_seo.docs_installed", "1")
        return existing
    return None

def post_init_hook(env):
    install_knowledge_docs(env)

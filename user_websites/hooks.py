# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import logging
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

def install_knowledge_docs(env):
    """
    Checks if the knowledge.article or manual.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    article_model_name = None
    if "knowledge.article" in env:
        article_model_name = "knowledge.article"
    elif "manual.article" in env:
        article_model_name = "manual.article"

    if article_model_name:
        utils = env["zero_sudo.security.utils"]

        # Dual service-account approach for strict least-privilege isolation
        param_svc_uid = utils._get_service_uid("user_websites.user_user_websites_service_account")
        doc_svc_uid = utils._get_service_uid("zero_sudo.odoo_facility_service_internal")

        if env["ir.config_parameter"].with_user(param_svc_uid).get_param("user_websites.docs_installed"):
            return None

        article_model = env[article_model_name].with_user(doc_svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "User Websites Documentation")], limit=1
        )

        if not existing:
            try:
                with file_open("user_websites/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                _logger.error("Failed to load user_websites documentation file: %s", e)
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "User Websites Documentation",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "category" in article_model._fields:
                vals["category"] = "workspace"
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🌐"

            try:
                article = article_model.create(vals)
                env["ir.config_parameter"].with_user(param_svc_uid).set_param("user_websites.docs_installed", "1")
                return article
            except Exception as e:
                _logger.error("Failed to create user_websites documentation article: %s", e)
        else:
            env["ir.config_parameter"].with_user(param_svc_uid).set_param("user_websites.docs_installed", "1")
        return existing
    return None

def post_init_hook(env):
    """
    Hook executed upon module installation.
    """
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "user_websites.user_user_websites_service_account"
    )

    user_group = env.ref(
        "user_websites.group_user_websites_user", raise_if_not_found=False
    )
    if user_group:
        user_group = user_group.with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )
        domain = [
            ("id", ">", 0),
            ("is_service_account", "!=", True),
        ]

        public_user = env.ref("base.public_user", raise_if_not_found=False)
        if public_user:
            domain.append(("id", "!=", public_user.id))

        users = (
            env["res.users"]
            .with_user(svc_uid)
            .with_context(active_test=False, mail_notrack=True, prefetch_fields=False)
            .search(domain, limit=100000)
        )
        user_group.write({"user_ids": [(4, u.id) for u in users]})

    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_website_page_published ON website_page (id) WHERE is_published = TRUE;"
    )
    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_blog_post_published ON blog_post (id) WHERE is_published = TRUE;"
    )

    # Lock down the Cloudflare service account (Hard Dependency)
    cf_svc = env.ref("cloudflare.user_cloudflare_service")
    if "is_service_account" in cf_svc._fields:
        cf_svc.with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        ).write({"is_service_account": True})

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
    # ADR-0055: Support soft dependencies on manual_library or enterprise knowledge.
    article_model_name = None
    if "knowledge.article" in env:
        article_model_name = "knowledge.article"
    elif "manual.article" in env:
        article_model_name = "manual.article"

    if article_model_name:
        # ADR-0055: Use system parameter to ensure idempotency and prevent redundant searches
        param_name = "user_websites.docs_installed"
        if env["ir.config_parameter"].sudo().get_param(param_name):  # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
            return None

        # ADR-0001/0055: We typically use service accounts, but since we have a soft
        # dependency on an external model (knowledge/manual), we cannot define a
        # permanent ACL in ir.model.access.csv.
        # To bypass this for documentation injection only, we use .sudo().
        article_model = env[article_model_name].sudo().with_context(  # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
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
            # Dynamically check for fields to ensure broad API compatibility
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
                env["ir.config_parameter"].sudo().set_param(param_name, "1")  # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
                return article
            except Exception as e:
                _logger.error("Failed to create user_websites documentation article: %s", e)
        else:
            env["ir.config_parameter"].sudo().set_param(param_name, "1")  # burn-ignore-sudo: ADR-0055 soft-dependency documentation bootstrap
        return existing
    return None


def post_init_hook(env):
    """
    Hook executed upon module installation.
    """
    # ADR-0001: Execute setup operations under the dedicated service account context
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "user_websites.user_user_websites_service_account"
    )

    # Enroll all existing users into the module's baseline security group
    # allowing them to interact with their Virtual Slug placeholders instantly.
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

        # Explicitly exclude the unauthenticated public guest user
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

    # Create partial indexes for highly-queried boolean states to optimize read performance
    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_website_page_published ON website_page (id) WHERE is_published = TRUE;"
    )
    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_blog_post_published ON blog_post (id) WHERE is_published = TRUE;"
    )

    # Soft-Dependency: Retroactively lock down the Cloudflare service account if it was installed first
    cf_svc = env.ref("cloudflare.user_cloudflare_service", raise_if_not_found=False)
    if cf_svc and "is_service_account" in cf_svc._fields:
        cf_svc.with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        ).write({"is_service_account": True})

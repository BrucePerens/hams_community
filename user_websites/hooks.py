# -*- coding: utf-8 -*-
from odoo.tools import file_open


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if "knowledge.article" in env:
        # ADR-0001: Execute setup operations under the dedicated service account context
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "user_websites.user_user_websites_service_account"
        )
        env_svc = env.with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        article_model = env_svc["knowledge.article"]
        existing = article_model.search(
            [("name", "=", "User Websites Documentation")], limit=1
        )

        if not existing:
            try:
                with file_open("user_websites/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
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

            return article_model.create(vals)
        return existing
    return None


def post_init_hook(env):
    """
    Hook executed upon module installation.
    Injects docs into the knowledge base if the API is already installed.
    """
    install_knowledge_docs(env)

    # ADR-0001: Execute setup operations under the dedicated service account context
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "user_websites.user_user_websites_service_account"
    )
    env_svc = env.with_user(svc_uid).with_context(
        mail_notrack=True, prefetch_fields=False
    )

    # Enroll all existing users into the module's baseline security group
    # allowing them to interact with their Virtual Slug placeholders instantly.
    user_group = env_svc.ref(
        "user_websites.group_user_websites_user", raise_if_not_found=False
    )
    if user_group:
        domain = [
            ("id", ">", 0),
            ("is_service_account", "!=", True),
        ]

        # Explicitly exclude the unauthenticated public guest user
        public_user = env_svc.ref("base.public_user", raise_if_not_found=False)
        if public_user:
            domain.append(("id", "!=", public_user.id))

        users = (
            env_svc["res.users"]
            .with_context(active_test=False)
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
    cf_svc = env_svc.ref("cloudflare.user_cloudflare_service", raise_if_not_found=False)
    if cf_svc and "is_service_account" in cf_svc._fields:
        cf_svc.write({"is_service_account": True})

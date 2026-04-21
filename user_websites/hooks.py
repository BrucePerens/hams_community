# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import logging

_logger = logging.getLogger(__name__)

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

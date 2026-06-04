# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    # [@ANCHOR: documentation_bootstrap]
    """
    Hook executed upon module installation.
    """
    user_group = env.ref(
        "user_websites.group_user_websites_user", raise_if_not_found=False
    )
    if user_group:
        domain = [
            ("id", ">", 0),
            ("is_service_account", "!=", True),
        ]

        public_user = env.ref("base.public_user", raise_if_not_found=False)
        if public_user:
            domain.append(("id", "!=", public_user.id))

        users = env["res.users"].with_context(active_test=False).search(domain, limit=100000)
        user_group.write({"user_ids": [(4, u.id) for u in users]})

    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_website_page_published ON website_page (id) WHERE is_published = TRUE;"
    )
    env.cr.execute(
        "CREATE INDEX IF NOT EXISTS idx_blog_post_published ON blog_post (id) WHERE is_published = TRUE;"
    )

    # Lock down the Cloudflare service account (Hard Dependency)
    cf_svc = env.ref("cloudflare.user_cloudflare_purge", raise_if_not_found=False)
    if cf_svc:
        cf_svc.write({"is_service_account": True})

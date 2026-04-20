# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. AGPL-3.0.
import os
import logging
from odoo.tools import misc

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    html_path = misc.file_path("distributed_redis_cache/data/documentation.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            body_html = f.read()

        # manual_library implements least-privilege architecture using a dedicated
        # micro-privilege service account (user_manual_library_service_account)
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "manual_library.user_manual_library_service_account"
        )
        env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        ).create(
            {
                "name": "Distributed Redis Cache",
                "body": body_html,
                "is_published": True,
                "internal_permission": "read",
            }
        )
        _logger.info("Successfully installed Distributed Redis Cache documentation.")

    if "daemon.key.registry" in env:
        env["daemon.key.registry"].register_daemon(
            daemon_name="Redis Cache Manager",
            user_xml_id="distributed_redis_cache.cache_manager_service_internal",
            env_file_path="/var/lib/odoo/daemon_keys/cache_manager.env",
        )
        _logger.info("Registered Redis Cache Manager daemon keys.")

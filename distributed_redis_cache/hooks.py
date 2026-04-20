# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. AGPL-3.0.
import logging
from odoo.tools import file_open, _

_logger = logging.getLogger(__name__)


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone HTML documentation file and installs it.
    """
    if "knowledge.article" in env:
        # manual_library implements least-privilege architecture using a dedicated
        # micro-privilege service account (user_manual_library_service_account).
        # We try to use it, otherwise fall back to odoo_facility_service_internal.
        try:
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "manual_library.user_manual_library_service_account"
            )
        except (KeyError, ValueError):
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "zero_sudo.odoo_facility_service_internal"
            )

        article_model = env["knowledge.article"].with_user(svc_uid).with_context(
            mail_notrack=True, prefetch_fields=False
        )

        existing = article_model.search(
            [("name", "=", "Distributed Redis Cache")], limit=1
        )

        if not existing:
            try:
                with file_open("distributed_redis_cache/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                _logger.error(_("Failed to load Distributed Redis Cache documentation file: %s"), e)
                doc_body = _("<p>Error loading documentation file: %s</p>") % e

            vals = {
                "name": "Distributed Redis Cache",
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
                vals["icon"] = "⚡"

            article_model.create(vals)
            _logger.info("Successfully installed Distributed Redis Cache documentation.")
        return existing
    return None


def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    # ADR-0055: Modules must have "soft" dependencies for documentation
    install_knowledge_docs(env)

    if "daemon.key.registry" in env:
        env["daemon.key.registry"].register_daemon(
            daemon_name="Redis Cache Manager",
            user_xml_id="distributed_redis_cache.cache_manager_service_internal",
            env_file_path="/var/lib/odoo/daemon_keys/cache_manager.env",
        )
        _logger.info("Registered Redis Cache Manager daemon keys.")

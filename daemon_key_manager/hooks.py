# -*- coding: utf-8 -*-
import os
import logging
from odoo import api, tools, _

_logger = logging.getLogger(__name__)


def install_knowledge_docs(env):
    """
    Checks if knowledge.article or manual.article APIs are present and installs docs.
    Supports soft dependencies and handles order of installation by being callable
    from both post_init_hook and _register_hook.
    """
    article_model = None
    if "knowledge.article" in env:
        article_model = "knowledge.article"
    elif "manual.article" in env:
        article_model = "manual.article"

    if not article_model:
        return

    try:
        # Use the standard facility service account for documentation installation
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
    except Exception:
        # Fallback to module-specific service account if the facility one isn't available
        try:
            svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "daemon_key_manager.user_daemon_key_manager_service"
            )
        except Exception:
            _logger.warning("Could not find service account for documentation installation.")
            return

    with_svc_env = env.user.with_user(svc_uid).with_context(
        mail_notrack=True, prefetch_fields=False
    ).env

    existing = with_svc_env[article_model].search(
        [("name", "=", "Daemon Key Manager Documentation")], limit=1
    )
    if existing:
        return

    doc_path = tools.misc.file_path("daemon_key_manager/LLM_DOCUMENTATION.md")
    if os.path.exists(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        vals = {
            "name": "Daemon Key Manager Documentation",
            "body": content,
        }
        # Dynamically check for fields to ensure broad API compatibility
        model_obj = with_svc_env[article_model]
        if "is_published" in model_obj._fields:
            vals["is_published"] = True
        if "internal_permission" in model_obj._fields:
            vals["internal_permission"] = "read"
        if "icon" in model_obj._fields:
            vals["icon"] = "🔑"

        try:
            with_svc_env[article_model].create(vals)
            _logger.info("Successfully installed Daemon Key Manager documentation.")
        except Exception as e:
            _logger.error("Failed to create documentation article: %s", e)


def post_init_hook(env):
    """
    Installs the module's LLM documentation.
    """
    install_knowledge_docs(env)

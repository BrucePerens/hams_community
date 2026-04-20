# -*- coding: utf-8 -*-
import logging
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the standalone documentation file and installs it.
    Supports both 'manual_library' (community) and 'knowledge' (enterprise).
    """
    # Check for either the community manual_library or the enterprise knowledge module
    model_name = "knowledge.article"
    if model_name not in env:
        return None

    # Use the odoo_facility_service_internal for general maintenance tasks
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "zero_sudo.odoo_facility_service_internal"
    )
    article_model = (
        env[model_name]
        .with_user(svc_uid)
        .with_context(mail_notrack=True, prefetch_fields=False)
    )

    existing = article_model.search(
        [("name", "=", "Cloudflare Edge Orchestration Documentation")], limit=1
    )

    if not existing:
        try:
            with file_open("cloudflare/data/documentation.md", "r") as f:
                doc_body = f.read()
            # Wrap markdown in a basic <pre> block for the Knowledge HTML body
            doc_body = f"<pre>{doc_body}</pre>"
        except Exception as e:
            _logger.error("Failed to load Cloudflare documentation file: %s", e)
            doc_body = f"<p>Error loading documentation file: {e}</p>"

        vals = {
            "name": "Cloudflare Edge Orchestration Documentation",
            "body": doc_body,
        }
        # Dynamically check for fields to ensure broad API compatibility
        if "is_published" in article_model._fields:
            vals["is_published"] = True
        if "internal_permission" in article_model._fields:
            vals["internal_permission"] = "read"
        if "icon" in article_model._fields:
            vals["icon"] = "☁️"
        if "category" in article_model._fields:
            # common in some versions of knowledge
            vals["category"] = "workspace"

        return article_model.create(vals)
    return existing


def post_init_hook(env):
    """
    Executes automatically upon module installation.
    Analyzes the Cloudflare perimeter and syncs or deploys the configuration natively.
    """
    _logger.info("Initializing Cloudflare Edge Orchestration...")

    # Execute Zero-Sudo invocation of the config manager
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "cloudflare.user_cloudflare_waf"
    )
    env["cloudflare.config.manager"].with_user(svc_uid).initialize_cloudflare_state()

    # NOTE: To fulfill the requirement of waiting until ALL modules are installed,
    # we rely on the fact that if manual_library or knowledge is present in the
    # environment during this post_init_hook, we install the docs.
    # In Odoo 19, hooks run at the end of the module installation process.
    install_knowledge_docs(env)

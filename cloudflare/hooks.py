# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def install_knowledge_docs(env):
    """
    Checks if the knowledge.article API is present in the environment.
    If it is, reads the LLM documentation file and installs it.
    """
    if "knowledge.article" in env:
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
        article_model = (
            env["knowledge.article"]
            .with_user(svc_uid)
            .with_context(mail_notrack=True, prefetch_fields=False)
        )

        existing = article_model.search(
            [("name", "=", "Cloudflare Edge Orchestration Documentation")], limit=1
        )

        if not existing:
            try:
                from odoo.tools import file_open  # noqa: E402

                with file_open("docs/modules/cloudflare.md", "r") as f:
                    doc_body = f.read()
                # Wrap markdown in a basic HTML body for the knowledge system
                doc_body = f"<pre>{doc_body}</pre>"
            except Exception as e:
                doc_body = f"<p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Cloudflare Edge Orchestration Documentation",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "☁️"

            return article_model.create(vals)
        return existing
    return None


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

    install_knowledge_docs(env)

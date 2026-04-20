# -*- coding: utf-8 -*-
import logging
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    # We use knowledge.article as the target for both manual_library and Enterprise knowledge
    if "knowledge.article" in env and "zero_sudo.security.utils" in env:
        # Try to use manual_library's service account if available, fallback to odoo_facility_service_internal
        utils = env["zero_sudo.security.utils"]
        svc_uid = utils._get_service_uid("manual_library.user_manual_library_service_account")
        if not svc_uid:
            svc_uid = utils._get_service_uid("zero_sudo.odoo_facility_service_internal")

        if svc_uid:
            env_svc = env.user.with_user(svc_uid).with_context(mail_notrack=True, prefetch_fields=False).env
            article_model = env_svc["knowledge.article"]

            existing = article_model.search([("name", "=", "Pager Duty & Generalized Monitoring")], limit=1)
            if not existing:
                try:
                    with file_open("pager_duty/data/documentation.html", "r", encoding="utf-8") as f:
                        body_html = f.read()

                    vals = {
                        "name": "Pager Duty & Generalized Monitoring",
                        "body": body_html,
                    }
                    # Broad API compatibility checks
                    if "is_published" in article_model._fields:
                        vals["is_published"] = True
                    if "internal_permission" in article_model._fields:
                        vals["internal_permission"] = "read"
                    if "icon" in article_model._fields:
                        vals["icon"] = "📟"

                    article_model.create(vals)
                except Exception as e:
                    _logger.warning("Could not install Pager Duty documentation: %s", e)

    # Trigger autodiscovery if the system is completely empty
    if "pager.check" in env and not env["pager.check"].search_count([]):
        try:
            env["pager.check"]._run_autodiscovery()
        except Exception as e:
            _logger.warning("An error occurred during autodiscovery: %s", e)

    # Register Daemons for Automated Key Vault Provisioning
    if "daemon.key.registry" in env:
        try:
            env["daemon.key.registry"].register_daemon(
                daemon_name="Pager Duty - Generalized Monitor",
                user_xml_id="pager_duty.user_pager_service_internal",
                env_file_path="/var/lib/odoo/daemon_keys/pager_duty.env",
            )
        except Exception as e:
            _logger.warning("An error occurred during daemon registration: %s", e)

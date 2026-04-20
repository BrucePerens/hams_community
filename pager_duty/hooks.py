# -*- coding: utf-8 -*-
def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    # Inject Knowledge Base Documentation
    import os  # noqa: E402
    from odoo.tools import misc  # noqa: E402

    html_path = misc.file_path("pager_duty/data/documentation.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            body_html = f.read()

        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
        env["knowledge.article"].with_user(svc_uid).create(
            {
                "name": "Pager Duty & Generalized Monitoring",
                "body": body_html,
                "is_published": True,
                "internal_permission": "read",
            }
        )

    # Trigger autodiscovery if the system is completely empty
    if "pager.check" in env and not env["pager.check"].search_count([]):
        try:
            env["pager.check"]._run_autodiscovery()
        except Exception as e:
            import logging  # noqa: E402
            logging.getLogger(__name__).warning("An error occurred during autodiscovery: %s", e)

    # Register Daemons for Automated Key Vault Provisioning
    if "daemon.key.registry" in env:
        try:
            env["daemon.key.registry"].register_daemon(
                daemon_name="Pager Duty - Generalized Monitor",
                user_xml_id="pager_duty.user_pager_service_internal",
                env_file_path="/var/lib/odoo/daemon_keys/pager_duty.env",
            )
        except Exception as e:
            import logging  # noqa: E402
            logging.getLogger(__name__).warning("An error occurred during daemon registration: %s", e)

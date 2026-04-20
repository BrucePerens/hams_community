# -*- coding: utf-8 -*-
def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    import os  # noqa: E402
    from odoo.tools import misc  # noqa: E402

    # Register Backup Worker for Automated Key Vault Provisioning
    # This remains as it depends on zero_sudo and internal logic
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
        "zero_sudo.odoo_facility_service_internal"
    )
    # Idiomatic Service Account Context (ADR-0001)
    env_svc = env.user.with_user(svc_uid).with_context(mail_notrack=True, prefetch_fields=False).env

    if "daemon.key.registry" in env:
        env_svc["daemon.key.registry"].register_daemon(
            daemon_name="Backup Worker RabbitMQ Consumer",
            user_xml_id="backup_management.backup_service_internal",
            env_file_path="/var/lib/odoo/daemon_keys/backup_worker.env",
        )

    # Soft documentation installation (manual_library OR knowledge)
    if "knowledge.article" in env:
        html_path = misc.file_path("backup_management/data/documentation.html")
        body_html = ""
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                body_html = f.read()

        if body_html:
            # Try to use manual_library service account if available, fallback to odoo_facility
            lib_svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
                "manual_library.user_manual_library_service_account"
            )
            if not lib_svc_uid:
                lib_svc_uid = svc_uid

            env_lib = env.user.with_user(lib_svc_uid).with_context(mail_notrack=True, prefetch_fields=False).env

            # Check if it already exists to avoid duplicates on re-install
            existing = env_lib["knowledge.article"].search([("name", "=", "Backup Management")], limit=1)
            if not existing:
                vals = {
                    "name": "Backup Management",
                    "body": body_html,
                }
                # Handle API differences if any (manual_library vs Odoo Enterprise Knowledge)
                if "is_published" in env_lib["knowledge.article"]._fields:
                    vals["is_published"] = True
                if "internal_permission" in env_lib["knowledge.article"]._fields:
                    vals["internal_permission"] = "read"

                env_lib["knowledge.article"].create(vals)

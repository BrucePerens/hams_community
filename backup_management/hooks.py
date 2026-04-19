def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    import os  # noqa: E402
    from odoo.tools import misc  # noqa: E402

    html_path = misc.file_path("backup_management/data/documentation.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            body_html = f.read()

        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
        env["knowledge.article"].with_user(svc_uid).create(
            {
                "name": "Backup Management",
                "body": body_html,
                "is_published": True,
                "internal_permission": "read",
            }
        )

    # Register Backup Worker for Automated Key Vault Provisioning
    if "daemon.key.registry" in env:
        env["daemon.key.registry"].register_daemon(
            daemon_name="Backup Worker RabbitMQ Consumer",
            user_xml_id="backup_management.backup_service_internal",
            env_file_path="/var/lib/odoo/daemon_keys/backup_worker.env",
        )

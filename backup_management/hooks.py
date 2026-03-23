def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    import os
    from odoo.tools import misc

    html_path = misc.file_path("backup_management/data/documentation.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            body_html = f.read()

        env["knowledge.article"].sudo().create(
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

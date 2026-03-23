def post_init_hook(env):
    """
    Inject documentation and register daemon keys upon installation.
    """
    import os
    from odoo.tools import misc

    html_path = misc.file_path("distributed_redis_cache/data/documentation.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            body_html = f.read()

        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "zero_sudo.odoo_facility_service_internal"
        )
        env["knowledge.article"].with_user(svc_uid).create(
            {
                "name": "Distributed Redis Cache",
                "body": body_html,
                "is_published": True,
                "internal_permission": "read",
            }
        )

    if "daemon.key.registry" in env:
        env["daemon.key.registry"].register_daemon(
            daemon_name="Redis Cache Manager",
            user_xml_id="distributed_redis_cache.cache_manager_service_internal",
            env_file_path="/var/lib/odoo/daemon_keys/cache_manager.env",
        )

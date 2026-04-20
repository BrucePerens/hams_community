# -*- coding: utf-8 -*-
import os
from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    html_path = os.path.join(os.path.dirname(__file__), "data", "documentation.html")
    if not os.path.exists(html_path):
        return
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Use the service account from manual_library to create the documentation
    # This follows the least-privilege principle for installing documentation.
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid("manual_library.user_manual_library_service_account")
    if svc_uid:
        # env.user.with_user(svc_uid).env is the correct idiom
        env_svc = env.user.with_user(svc_uid).with_context(mail_notrack=True, prefetch_fields=False).env
        if "knowledge.article" in env_svc:
            env_svc["knowledge.article"].create({"name": "Binary Downloader", "body": content})

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Refactoring Tool: Proprietary SRE to Open Source Community
----------------------------------------------------------------------
Extracts ham_backup_management, ham_database_management, and ham_pager_duty
into standalone AGPL-3 modules in the hams_community repository.

It automatically renames directories, files, SQL tables, ORM models, and JS namespaces,
strips the ham_base dependency, and injects localized mail service accounts to
maintain Zero-Sudo security without external entanglements.
"""

import os
import shutil
import re

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEST_DIR = os.path.abspath(os.path.join(SRC_DIR, "..", "hams_community"))

MODULES = {
    "backup_management": "backup_management",
    "database_management": "database_management",
    "pager_duty": "pager_duty",
}

REPLACEMENTS = [
    (r"['\"]ham_base['\"]\s*,\s*", ""),
    (r"['\"]Proprietary['\"]", "'AGPL-3'"),
    (
        r"Copyright © Bruce Perens K6BP\. All Rights Reserved\. This software is proprietary and confidential\.",
        "Copyright © Bruce Perens K6BP. AGPL-3.0.",
    ),
    (
        r"Copyright © Bruce Perens K6BP\. All Rights Reserved\.",
        "Copyright © Bruce Perens K6BP. AGPL-3.0.",
    ),
    (r"['\"]post_init_hook['\"]\s*:\s*['\"]post_init_hook['\"]\s*,?", ""),
    (r"ham_backup_management", "backup_management"),
    (r"ham_database_management", "database_management"),
    (r"ham_pager_duty", "pager_duty"),
    (r"ham_backup_", "backup_"),
    (r"ham_database_", "database_"),
    (r"ham_pager_", "pager_"),
    (r"ham_pg_", "pg_"),
    (r"ham\.backup\.", "backup."),
    (r"ham\.database\.", "database."),
    (r"ham\.pg\.", "pg."),
    (r"ham\.pager\.", "pager."),
    (r"ham_base\.menu_ham_admin_root", "menu_admin_root"),
    (r"ham_base\.menu_ham_admin_health", "menu_admin_root"),
    (r"ham_base\.user_mail_service", "user_mail_service_internal"),
    (r"ham_base\.group_mail_service", "group_mail_service"),
]


def patch_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    for pattern, repl in REPLACEMENTS:
        content = re.sub(pattern, repl, content)
    if filepath.endswith("__init__.py"):
        content = re.sub(r"from \.hooks import post_init_hook\n?", "", content)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def inject_mail_service(module_dest):
    sec_xml = os.path.join(module_dest, "security", "security.xml")
    if os.path.exists(sec_xml):
        with open(sec_xml, "r", encoding="utf-8") as f:
            content = f.read()
        if "group_mail_service" not in content:
            mod_name = os.path.basename(module_dest)
            addition = f"""
        <record id="group_mail_service" model="res.groups">
            <field name="name">Local Mail Service Account</field>
        </record>
        <record id="user_mail_service_internal" model="res.users">
            <field name="name">{mod_name.replace("_", " ").title()} Mailer</field>
            <field name="login">{mod_name}_mail_service_internal</field>
            <field name="is_service_account" eval="True"/>
            <field name="group_ids" eval="[(6, 0, [ref('{mod_name}.group_mail_service'), ref('base.group_user')])]"/>
        </record>
"""
            content = content.replace("</data>", addition + "    </data>")
            with open(sec_xml, "w", encoding="utf-8") as f:
                f.write(content)


def patch_incident_redis(module_dest):
    inc_py = os.path.join(module_dest, "models", "incident.py")
    if os.path.exists(inc_py):
        with open(inc_py, "r", encoding="utf-8") as f:
            content = f.read()
        redis_import = "from odoo.addons.distributed_redis_cache.redis_pool import redis, redis_pool"
        redis_inline = """import os
import logging
_logger = logging.getLogger(__name__)
try:
    import redis
    redis_host = os.getenv('REDIS_HOST', '127.0.0.1')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0, decode_responses=True)
except ImportError:
    redis = None
    redis_pool = None
"""
        content = content.replace(redis_import, redis_inline)
        with open(inc_py, "w", encoding="utf-8") as f:
            f.write(content)


def patch_generalized_monitor(module_dest):
    gen_py = os.path.join(
        module_dest, "daemons", "pager_duty", "generalized_monitor.py"
    )
    if os.path.exists(gen_py):
        with open(gen_py, "r", encoding="utf-8") as f:
            content = f.read()
        config_import = "from hams_config import get_odoo_client"
        config_inline = """def get_odoo_client(logger=None):
    import xmlrpc.client
    import sys
    ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
    ODOO_DB = os.getenv('ODOO_DB', 'odoo')
    ODOO_USER = os.getenv('ODOO_USER', 'admin')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')
    class OdooClient:
        def __init__(self):
            self.common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            try:
                self.uid = self.common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
                if not self.uid: raise ValueError("Auth Failed")
                self.models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            except Exception as e:
                if logger: logger.critical(f"Auth Failed: {e}")
                sys.exit(1)
        def execute(self, model, method, *args, **kwargs):
            return self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, model, method, args, kwargs)
    return OdooClient()
"""
        content = content.replace(config_import, config_inline)
        content = re.sub(
            r"sys\.path\.append\(os\.path\.abspath\(os\.path\.join\(os\.path\.dirname\(__file__\), '\.\.'\)\)\)\n",
            "",
            content,
        )
        with open(gen_py, "w", encoding="utf-8") as f:
            f.write(content)


def patch_menus(module_dest):
    menu_xml = os.path.join(module_dest, "views", "menu_views.xml")
    if os.path.exists(menu_xml):
        with open(menu_xml, "r", encoding="utf-8") as f:
            content = f.read()
        if (
            "menu_admin_root" in content
            and '<menuitem id="menu_admin_root"' not in content
        ):
            mod_name = "Database &amp; SRE"
            if "backup" in module_dest:
                mod_name = "Backups"
            elif "pager" in module_dest:
                mod_name = "Pager Duty"
            addition = (
                f'<menuitem id="menu_admin_root" name="{mod_name}" sequence="70"/>\n'
            )
            content = content.replace("<odoo>", f"<odoo>\n    {addition}")
        with open(menu_xml, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    for src_mod, dest_mod in MODULES.items():
        src = os.path.join(SRC_DIR, src_mod)
        dest = os.path.join(DEST_DIR, dest_mod)
        if not os.path.exists(src):
            continue
        if os.path.exists(dest):
            shutil.rmtree(dest)
        print(f"[*] Copying {src_mod} -> {dest_mod}...")
        shutil.copytree(src, dest)

        for root, dirs, files in os.walk(dest, topdown=False):
            for name in files:
                if name.startswith("ham_"):
                    os.rename(
                        os.path.join(root, name),
                        os.path.join(root, name.replace("ham_", "", 1)),
                    )
            for name in dirs:
                if name.startswith("ham_"):
                    os.rename(
                        os.path.join(root, name),
                        os.path.join(root, name.replace("ham_", "", 1)),
                    )

        hooks_py = os.path.join(dest, "hooks.py")
        if os.path.exists(hooks_py):
            os.remove(hooks_py)

        for root, _, files in os.walk(dest):
            for file in files:
                if file.endswith((".py", ".xml", ".js", ".csv")):
                    patch_file(os.path.join(root, file))

        inject_mail_service(dest)
        patch_menus(dest)
        if dest_mod == "pager_duty":
            patch_incident_redis(dest)
            patch_generalized_monitor(dest)


if __name__ == "__main__":
    main()

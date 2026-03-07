#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from odoo import models, api, tools, _
from odoo.exceptions import AccessError, UserError

PARAM_WHITELIST = frozenset(
    [
        "web.base.url",
        "cloudflare.last_static_mtime",
        "user_websites.last_digest_key",
        "user_websites.last_digest_id",
        "user_websites.global_website_page_limit",
        "user_websites.company_abuse_email",
        "cloudflare.turnstile_secret",
    ]
)

class ZeroSudoSecurityUtils(models.AbstractModel):
    _name = "zero_sudo.security.utils"
    _description = "Centralized Security and Privilege Utilities"

    @api.model
    def _get_deterministic_hash(self, input_string):
        """
        Generates a high-speed, deterministic 32-bit integer hash.
        Used primarily for PostgreSQL advisory locks (pg_advisory_xact_lock).
        """
        if not isinstance(input_string, str):
            input_string = str(input_string)
        return (
            int(hashlib.sha256(input_string.encode("utf-8")).hexdigest()[:8], 16)
            % 2147483647
        )

    @api.model
    @tools.ormcache("xml_id")
    def _get_service_uid(self, xml_id):
        # [%ANCHOR: get_service_uid]
        uid = self.env["ir.model.data"].sudo()._xmlid_to_res_id(xml_id)
        if not uid:
            raise AccessError(
                _("Security Alert: Service Account '%s' not found.") % xml_id
            )
        self.env.cr.execute("SELECT active FROM res_users WHERE id = %s", (uid,))
        res = self.env.cr.fetchone()
        if not res or not res[0]:
            raise AccessError(_("Security Alert: Service Account is disabled."))
        return uid

    @api.model
    def _notify_cache_invalidation(self, model_name, key_value):
        # [%ANCHOR: coherent_cache_signal]
        if isinstance(key_value, (list, set, tuple)):
            payloads = [f"{model_name}:{kv}" for kv in set(key_value) if kv]
            if payloads:
                self.env.cr.execute(
                    "SELECT pg_notify(%s, payload) FROM unnest(%s) AS payload",
                    ("cache_invalidation", payloads),
                )
        else:
            self.env.cr.execute(
                "SELECT pg_notify(%s, %s)",
                ("cache_invalidation", f"{model_name}:{key_value}"),
            )

    @api.model
    def _get_system_param(self, key, default=None):
        if key not in PARAM_WHITELIST:
            raise AccessError(
                _("Security Alert: Parameter '%s' is not whitelisted for extraction.")
                % key
            )
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    @api.model
    def _update_python_venv(self):
        req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "requirements.txt"))
        if not os.path.exists(req_path):
            raise UserError(_("Requirements file not found at %s") % req_path)

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_path],
                capture_output=True,
                text=True,
                check=True,
                shell=False
            )
            return True
        except subprocess.CalledProcessError as e:
            raise UserError(_("VENV update failed:\n%s") % e.stderr)

    @api.model
    def _ensure_executable(self, cmd_name):
        path = shutil.which(cmd_name)
        if path:
            return path

        manifest_record = self.env["zero_sudo.binary.manifest"].search([("name", "=", cmd_name)], limit=1)
        if not manifest_record:
            raise UserError(_("Missing dependency: '%s'. Please configure it in Settings -> Technical -> Binary Manifests or install via OS package manager.") % cmd_name)

        if platform.system() != "Linux" or platform.machine() != "x86_64":
            raise UserError(_("Auto-install of %s is only supported on Linux x86_64. Please install manually.") % cmd_name)

        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        bin_dir = os.path.join(data_dir, "hams_bin")

        os.makedirs(bin_dir, exist_ok=True)
        os.chmod(bin_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

        target_bin = os.path.join(bin_dir, cmd_name)

        if os.path.exists(target_bin):
            os.chmod(target_bin, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            return target_bin

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                urllib.request.urlretrieve(manifest_record.url, tmp.name)

            hasher = hashlib.sha256()
            with open(tmp.name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)

            if hasher.hexdigest() != manifest_record.checksum:
                os.unlink(tmp.name)
                raise UserError(_("Security Alert: Checksum mismatch for downloaded %s binary.") % cmd_name)

            if manifest_record.archive_type == "tar.gz":
                with tarfile.open(tmp.name, "r:gz") as tar:
                    for member in tar.getmembers():
                        extract_target = manifest_record.extract_member or cmd_name
                        if member.name.endswith(f"/{extract_target}") or member.name == extract_target:
                            member.name = cmd_name
                            tar.extract(member, path=bin_dir)
                            break
            else:
                shutil.copy2(tmp.name, target_bin)

            os.chmod(target_bin, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            os.unlink(tmp.name)
            return target_bin
        except Exception as e:
            raise UserError(_("Failed to auto-install %s: %s") % (cmd_name, str(e)))

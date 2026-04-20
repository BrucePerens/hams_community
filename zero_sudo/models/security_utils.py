# -*- coding: utf-8 -*-
import hashlib
import os
import subprocess
import sys
from odoo import models, api, tools, _
from odoo.exceptions import AccessError, UserError


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
        # [@ANCHOR: get_service_uid]
        # Verified by [@ANCHOR: test_get_service_uid]
        uid = self.env["ir.model.data"].sudo()._xmlid_to_res_id(xml_id)
        if not uid:
            raise AccessError(
                _("Security Alert: Service Account '%s' not found.") % xml_id
            )

        # Verify the account is active AND is explicitly flagged as a service account
        self.env.cr.execute(
            "SELECT active, is_service_account FROM res_users WHERE id = %s", (uid,)
        )
        res = self.env.cr.fetchone()

        if not res or not res[0]:
            raise AccessError(_("Security Alert: Service Account is disabled."))
        if not res[1]:
            raise AccessError(
                _(
                    "Security Alert: '%s' is a human user, not a Service Account. Privilege escalation denied."
                )
                % xml_id
            )

        # THE MECHANICAL GOD-MODE BLOCK: Ensure the service account does not possess global administrative privileges.
        # This mathematically forces downstream modules to utilize the Micro-Service Account CSV pattern.
        self.env.cr.execute(
            """
            SELECT 1 FROM res_groups_users_rel rel
            JOIN ir_model_data imd ON imd.res_id = rel.gid AND imd.model = 'res.groups'
            WHERE rel.uid = %s AND imd.module = 'base' AND imd.name IN ('group_system', 'group_erp_manager')
        """,
            (uid,),
        )

        if self.env.cr.fetchone():
            raise AccessError(
                _(
                    "Security Alert: Service Account '%s' violates the Zero-Sudo mandate by possessing global administrative groups (group_system or group_erp_manager). You must use domain-specific Micro-Privilege ACLs instead."
                )
                % xml_id
            )

        return uid

    @api.model
    def _notify_cache_invalidation(self, model_name, key_value):
        # [@ANCHOR: coherent_cache_signal]
        # Verified by [@ANCHOR: test_coherent_cache_signal]
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
        # THE MECHANICAL SECRET BLOCK
        # Prevents Server-Side Template Injection (SSTI) from exfiltrating sensitive keys.
        # This implementation uses a dual-protection strategy:
        # 1. A hardcoded PARAM_WHITELIST (ADR-0002)
        # 2. A mechanical block on sensitive substrings for dynamic keys.

        PARAM_WHITELIST = [
            "web.base.url",
            "cloudflare.last_static_mtime",
            "user_websites.company_abuse_email",
            "user_websites.max_sites_per_user",
            "user_websites.enable_blog_comments",
            "caching.safe_quota_mb",
            "caching.invalidation_version",
            "user_websites.global_website_page_limit",
            "user_websites.last_digest_id",
            "user_websites_seo.docs_installed",
        ]

        banned_substrings = [
            "secret",
            "key",
            "password",
            "token",
            "auth",
            "crypt",
            "cert",
        ]
        lower_key = key.lower()

        if key not in PARAM_WHITELIST:
            # If not in whitelist, we check if it's a dynamic key or if it contains banned substrings.
            # For strict compliance with ADR-0002, we should ideally ONLY allow whitelisted keys.
            if any(banned in lower_key for banned in banned_substrings):
                raise AccessError(
                    _(
                        "Security Alert: Parameter '%s' matches restricted cryptographic patterns and cannot be extracted via Zero-Sudo."
                    )
                    % key
                )

            # In some cases, we might want to allow non-whitelisted but safe keys for decentralization,
            # but the documentation explicitly states "The requested key MUST be hardcoded in the PARAM_WHITELIST".
            # To be safe and compliant, we enforce the whitelist strictly.
            raise AccessError(
                _(
                    "Security Alert: Parameter '%s' is not in the Zero-Sudo PARAM_WHITELIST. You must explicitly register it in zero_sudo/models/security_utils.py."
                )
                % key
            )

        # burn-ignore-sudo: Tested by [@ANCHOR: test_01_mechanical_secret_block_enforcement]
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    @api.model
    def _update_python_venv(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can update the Python environment."))

        req_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "requirements.txt")
        )
        if not os.path.exists(req_path):
            raise UserError(_("Requirements file not found at %s") % req_path)

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_path],
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise UserError(_("VENV update failed:\n%s") % e.stderr)

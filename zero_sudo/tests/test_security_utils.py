#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError
from unittest.mock import patch


@tagged("post_install", "-at_install")
class TestSecurityUtils(TransactionCase):

    def test_01_mechanical_secret_block_enforcement(self):
        """Verify that parameters matching cryptographic patterns are blocked."""
        utils = self.env["zero_sudo.security.utils"]

        # Safe parameters should pass
        base_url = utils._get_system_param("web.base.url")
        self.assertTrue(base_url is not None or base_url is False)

        # Dangerous parameters MUST be violently rejected
        dangerous_keys = [
            "database.secret",
            "my_api_key",
            "admin_password",
            "oauth_token",
            "cert_file",
        ]
        for key in dangerous_keys:
            with self.assertRaises(
                AccessError,
                msg=f"Extracting dangerous param '{key}' MUST raise an AccessError.",
            ):
                utils._get_system_param(key)

    def test_02_bdd_ormcache_query_counting_service_uid(self):
        # [@ANCHOR: test_get_service_uid]
        # Tests [@ANCHOR: get_service_uid]
        from unittest.mock import patch

        utils = self.env["zero_sudo.security.utils"]

        # We must test using a valid Service Account, as the utility
        # violently rejects human users like 'base.user_admin'
        svc_xml_id = "zero_sudo.mail_service_internal"

        utils._get_service_uid(svc_xml_id)

        with patch.object(
            self.env.cr, "execute", wraps=self.env.cr.execute
        ) as mock_execute:
            utils._get_service_uid(svc_xml_id)
            for call in mock_execute.call_args_list:
                self.assertNotIn("res_users", call[0][0])

    def test_03_bdd_event_bus_payload_generation(self):
        # [@ANCHOR: test_coherent_cache_signal]
        # Tests [@ANCHOR: coherent_cache_signal]
        utils = self.env["zero_sudo.security.utils"]
        with patch.object(self.env.cr, "execute") as mock_execute:
            utils._notify_cache_invalidation("test.model", "test_key")
            mock_execute.assert_called_once_with(
                "SELECT pg_notify(%s, %s)",
                ("cache_invalidation", "test.model:test_key"),
            )

    def test_04_god_mode_block_enforcement(self):
        """Verify that any Service Account granted base.group_system is violently rejected."""
        # 1. Create a rogue service account
        rogue_user = self.env["res.users"].create(
            {
                "name": "Rogue God Account",
                "login": "rogue_god",
                "is_service_account": True,
                "group_ids": [(4, self.env.ref("base.group_system").id)],
            }
        )

        # 2. Bind it to an XML ID so _get_service_uid can look it up
        self.env["ir.model.data"].create(
            {
                "module": "rogue_module",
                "name": "sneaky_admin_service",
                "model": "res.users",
                "res_id": rogue_user.id,
            }
        )

        utils = self.env["zero_sudo.security.utils"]
        with self.assertRaises(
            AccessError,
            msg="Must block Service Accounts with group_system from escalating privileges.",
        ):
            utils._get_service_uid("rogue_module.sneaky_admin_service")

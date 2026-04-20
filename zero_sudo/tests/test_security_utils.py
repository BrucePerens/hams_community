# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError
from unittest.mock import patch


@tagged("post_install", "-at_install")
class TestSecurityUtils(TransactionCase):

    def test_01_mechanical_secret_block_enforcement(self):
        # [@ANCHOR: test_01_mechanical_secret_block_enforcement]
        # Tests [@ANCHOR: get_system_param]
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

        # Non-whitelisted safe parameters MUST also be rejected
        with self.assertRaises(
            AccessError,
            msg="Extracting non-whitelisted param MUST raise an AccessError.",
        ):
            utils._get_system_param("some.unregistered.safe.param")

    def test_02_bdd_ormcache_query_counting_service_uid(self):
        # [@ANCHOR: test_get_service_uid]
        # Tests [@ANCHOR: get_service_uid]
        from unittest.mock import patch  # noqa: E402

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

    def test_05_notify_cache_invalidation_list(self):
        """Test _notify_cache_invalidation with a list payload."""
        utils = self.env["zero_sudo.security.utils"]
        with patch.object(self.env.cr, "execute") as mock_execute:
            utils._notify_cache_invalidation("test.model", ["key1", "key2", "key1"])

            # Extract the arguments passed to execute
            args, _ = mock_execute.call_args
            query = args[0]
            params = args[1]

            self.assertEqual(query, "SELECT pg_notify(%s, payload) FROM unnest(%s) AS payload")
            self.assertEqual(params[0], "cache_invalidation")
            # We must sort the payloads because set conversion makes the order non-deterministic
            self.assertListEqual(sorted(params[1]), sorted(["test.model:key1", "test.model:key2"]))

    def test_06_get_deterministic_hash(self):
        # [@ANCHOR: test_deterministic_hash]
        # Tests [@ANCHOR: deterministic_hash]
        """Verify _get_deterministic_hash generates consistent integer hashes."""
        utils = self.env["zero_sudo.security.utils"]

        hash1 = utils._get_deterministic_hash("test_string_1")
        hash2 = utils._get_deterministic_hash("test_string_1")
        hash3 = utils._get_deterministic_hash("test_string_2")
        hash4 = utils._get_deterministic_hash(12345)

        self.assertIsInstance(hash1, int)
        self.assertEqual(hash1, hash2, "Same input should yield same hash")
        self.assertNotEqual(hash1, hash3, "Different inputs should yield different hashes")
        self.assertIsInstance(hash4, int, "Should handle non-string inputs gracefully")
        self.assertTrue(0 <= hash1 <= 2147483647, "Hash should be within 32-bit integer range")

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_07_update_python_venv(self, mock_exists, mock_run):
        # [@ANCHOR: test_update_python_venv]
        # Tests [@ANCHOR: update_python_venv]
        """Test the _update_python_venv method."""
        from odoo.exceptions import UserError  # noqa: E402
        utils = self.env["zero_sudo.security.utils"]

        # Test 1: requirements.txt not found
        mock_exists.return_value = False
        with self.assertRaises(UserError):
            utils._update_python_venv()

        # Test 2: requirements.txt exists, subprocess succeeds
        mock_exists.return_value = True
        mock_run.return_value.returncode = 0
        self.assertTrue(utils._update_python_venv())

        # Test 3: subprocess fails
        import subprocess  # noqa: E402
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="pip error")
        with self.assertRaises(UserError) as cm:
            utils._update_python_venv()
        self.assertIn("pip error", str(cm.exception))

        # Test 4: AccessError for non-admin
        non_admin = self.env["res.users"].create({
            "name": "Non Admin",
            "login": "non_admin_no_groups",
        })
        with self.assertRaises(AccessError):
            utils.with_user(non_admin)._update_python_venv()

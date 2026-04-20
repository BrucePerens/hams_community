# -*- coding: utf-8 -*-
import os
import tarfile
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged("post_install", "-at_install")
class TestBinaryManifest(TransactionCase):

    def tearDown(self):
        if os.path.exists("/var/lib/odoo/hams_bin/fake"):
            try:
                os.remove("/var/lib/odoo/hams_bin/fake")
            except OSError:
                pass
        super().tearDown()

    def setUp(self):
        super().setUp()
        if os.path.exists("/var/lib/odoo/hams_bin/fake"):
            try:
                os.remove("/var/lib/odoo/hams_bin/fake")
            except OSError:
                pass
        # The service account is already created by security.xml data
        self.service_user = self.env.ref("binary_downloader.user_binary_downloader_service")

        self.manifest = self.env["binary.manifest"].create(
            {
                "name": "testbin",
                "url": "http://example.com/testbin",
                "checksum": "fakehash",
                "archive_type": "binary",
            }
        )

    @patch("shutil.which")
    def test_01_already_installed(self, mock_which):
        # Tests [@ANCHOR: binary_ensure_executable]
        # Tests [@ANCHOR: binary_resolution]
        """Verify it returns the system path immediately if the binary is found."""
        mock_which.return_value = "/usr/bin/testbin"
        path = self.env["binary.manifest"].ensure_executable("testbin")
        self.assertEqual(path, "/usr/bin/testbin")
        mock_which.assert_called_once_with("testbin")

    @patch("shutil.which", return_value=None)
    def test_02_missing_manifest(self, mock_which):
        """Verify it raises an error if the binary is missing and not configured in the DB."""
        with self.assertRaises(UserError, msg="Must raise error on missing manifest"):
            self.env["binary.manifest"].ensure_executable("missingbin")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Windows")
    def test_03_unsupported_platform(self, mock_system, mock_which):
        """Verify it actively blocks auto-installations on non-Linux architectures."""
        with self.assertRaises(UserError, msg="Must block non-Linux platforms"):
            self.env["binary.manifest"].ensure_executable("testbin")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Linux")
    @patch("platform.machine", return_value="x86_64")
    @patch("urllib.request.urlretrieve")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.chmod")
    @patch("os.makedirs")
    def test_04_successful_download_and_checksum(
        self,
        mock_makedirs,
        mock_chmod,
        mock_open,
        mock_urlretrieve,
        mock_machine,
        mock_system,
        mock_which,
    ):
        """Verify the downloading logic executes correctly with a valid checksum match."""
        with patch("hashlib.sha256") as mock_sha256:
            # Mock the cryptographic hasher to return our expected token
            mock_hasher = MagicMock()
            mock_hasher.hexdigest.return_value = "fakehash"
            mock_sha256.return_value = mock_hasher

            # Prevent physical file reads during the chunk validation loop
            mock_open.return_value.__enter__.return_value.read.side_effect = [
                b"chunk",
                b"",
            ]

            original_exists = os.path.exists

            def mock_exists(path):
                if "hams_bin/testbin" in path:
                    return False
                return original_exists(path)

            with patch("os.path.exists", side_effect=mock_exists):
                with patch("tempfile.NamedTemporaryFile") as mock_temp:
                    mock_temp_inst = MagicMock()
                    mock_temp_inst.name = "/var/lib/odoo/hams_bin/fake"
                    mock_temp.return_value.__enter__.return_value = mock_temp_inst
                    with patch("shutil.copy2") as mock_copy, patch("os.unlink"):
                        path = self.env["binary.manifest"].ensure_executable("testbin")
                        self.assertTrue(path.endswith("testbin"))
                        mock_urlretrieve.assert_called_once()
                        mock_copy.assert_called_once()

    def test_05_views_render(self):
        # Tests [@ANCHOR: test_binary_manifest_views]
        """Verify that standard backend views compile without error."""
        v1 = self.env["binary.manifest"].get_view(view_type="list")
        self.assertIn("name", v1["arch"])

        v2 = self.env["binary.manifest"].get_view(view_type="form")
        self.assertIn("url", v2["arch"])

    @patch("shutil.which")
    def test_06_is_installed_compute(self, mock_which):
        # Tests [@ANCHOR: binary_compute_installed]
        """Verify the is_installed compute field logic."""
        mock_which.return_value = "/usr/bin/testbin"
        self.assertTrue(self.manifest.is_installed)

        self.manifest.invalidate_recordset(['is_installed'])
        mock_which.return_value = None
        with patch("os.path.exists", return_value=False):
            self.assertFalse(self.manifest.is_installed)

    @patch("odoo.addons.binary_downloader.models.binary_manifest.BinaryManifest.ensure_executable")
    def test_07_action_install(self, mock_ensure):
        # Tests [@ANCHOR: binary_action_install]
        """Verify the action_install method calls ensure_executable and returns a notification."""
        result = self.manifest.action_install()
        mock_ensure.assert_called_once_with("testbin")
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")

    def test_08_path_traversal_validation(self):
        """Verify that slashes in the name are rejected to prevent path traversal."""
        with self.assertRaises(ValidationError):
            self.env["binary.manifest"].create({
                "name": "../badbin",
                "url": "http://example.com/badbin",
                "checksum": "fakehash",
                "archive_type": "binary",
            })

        with self.assertRaises(ValidationError):
            self.manifest.write({"name": "bad/bin"})

    def test_09_post_init_hook_documentation(self):
        # Tests [@ANCHOR: binary_doc_bootstrap]
        """Verify that the post_init_hook correctly creates documentation."""
        # Find the article created by the hook (it might already exist if tests run in certain order)
        article_model = self.env.get("knowledge.article")
        if not article_model:
            return  # Skip if manual_library isn't fully loaded or mockable here

        article = article_model.search([("name", "=", "Binary Downloader Facility")], limit=1)
        self.assertTrue(article, "Documentation article should have been created by post_init_hook")
        self.assertIn("Binary Downloader Facility", article.body)

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Linux")
    @patch("platform.machine", return_value="x86_64")
    @patch("urllib.request.urlretrieve")
    def test_10_tar_slip_prevention(self, mock_urlretrieve, mock_machine, mock_system, mock_which):
        """Verify that tar slip attempts are blocked."""
        self.env["binary.manifest"].create({
            "name": "slippy",
            "url": "http://example.com/slippy.tar.gz",
            "checksum": "fakehash_tar",
            "archive_type": "tar.gz",
            "extract_member": "slippy"
        })

        with patch("hashlib.sha256") as mock_sha256, \
             patch("tarfile.open") as mock_tar_open, \
             patch("builtins.open", new_callable=MagicMock) as mock_open:

            mock_hasher = MagicMock()
            mock_hasher.hexdigest.return_value = "fakehash_tar"
            mock_sha256.return_value = mock_hasher

            mock_open.return_value.__enter__.return_value.read.side_effect = [b"data", b""]

            # Mock tar member with malicious path
            mock_member = MagicMock()
            mock_member.name = "slippy" # It MUST match the extract_target to proceed to extraction

            mock_tar = MagicMock()
            mock_tar.getmembers.return_value = [mock_member]

            def mock_extract(member, path=None, filter=None):
                # Simulate the path traversal check
                # Note: in real code, member.name is modified to os.path.basename(cmd_name)
                # but we want to test the case where it's NOT modified correctly or the check catches it.
                pass
            mock_tar_open.return_value.__enter__.return_value = mock_tar

            # Mock os.path.exists to simulate file missing
            with patch("os.path.exists", return_value=False), \
                 patch("tempfile.NamedTemporaryFile") as mock_temp:

                mock_temp_inst = MagicMock()
                mock_temp_inst.name = "/var/lib/odoo/hams_bin/fake_tar"
                mock_temp.return_value.__enter__.return_value = mock_temp_inst

                # Ensure hasattr(tarfile, 'data_filter') returns False for this test to trigger fallback
                # We mock os.path.abspath to return something outside the bin_dir when member.name is used
                def mock_abspath(p):
                    if "hams_bin/slippy" in p:
                        return "/etc/passwd"
                    return p

                with patch("os.path.abspath", side_effect=mock_abspath), \
                     patch("os.unlink"):
                    if hasattr(tarfile, 'data_filter'):
                         # If it HAS data_filter, we need to mock it NOT having it or test that it uses it.
                         # But easier to just test our fallback logic if we can.
                         # Patching builtins.hasattr is a bit risky but we can try patching it where it's used.
                         with patch("odoo.addons.binary_downloader.models.binary_manifest.hasattr", side_effect=lambda obj, name: False if name == 'data_filter' else hasattr(obj, name)):
                             with self.assertRaisesRegex(UserError, "Security Alert: Tar slip attempt detected."):
                                 self.env["binary.manifest"].ensure_executable("slippy")
                    else:
                         with self.assertRaisesRegex(UserError, "Security Alert: Tar slip attempt detected."):
                             self.env["binary.manifest"].ensure_executable("slippy")

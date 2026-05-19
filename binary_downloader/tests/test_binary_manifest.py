# -*- coding: utf-8 -*-
import hashlib
import os
import tarfile
import stat
from unittest.mock import patch, MagicMock
from odoo import tools
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError

INTEGRATION_MODE = os.environ.get("HAMS_INTEGRATION_MODE") == "1"

def mock_if_standard(target, **kwargs):
    """Bypasses the mock if the runner is executing an integration test."""
    if INTEGRATION_MODE:
        def decorator(func):
            return func
        return decorator
    return patch(target, **kwargs)

@tagged("post_install", "-at_install", "integration" if INTEGRATION_MODE else "standard")
class TestBinaryManifest(TransactionCase):

    def tearDown(self):
        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        bin_dir = os.path.join(data_dir, "hams_bin")
        for path in [os.path.join(bin_dir, "fake"), os.path.join(bin_dir, "testbin"), os.path.join(bin_dir, "slippy"), os.path.join(bin_dir, "symlinkbin")]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        super().tearDown()

    def setUp(self):
        super().setUp()
        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        bin_dir = os.path.join(data_dir, "hams_bin")
        for path in [os.path.join(bin_dir, "fake"), os.path.join(bin_dir, "testbin"), os.path.join(bin_dir, "slippy"), os.path.join(bin_dir, "symlinkbin")]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        self.service_user = self.env.ref("binary_downloader.user_binary_downloader_service")

        if INTEGRATION_MODE:
            # Leverage the Dummy UI Tour HTTP controller to physically simulate the download process
            base_url = os.environ.get("ODOO_URL", "http://odoo:8069")
            url = f"{base_url}/test/dummy_bin"
            chksum = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
        else:
            url = "http://example.com/testbin"
            chksum = hashlib.sha256(b"chunk").hexdigest()

        self.manifest = self.env["binary.manifest"].create(
            {
                "name": "testbin",
                "url": url,
                "checksum": chksum,
                "archive_type": "binary",
            }
        )

    @mock_if_standard("shutil.which")
    def test_01_already_installed(self, mock_which=None):
        # [@ANCHOR: test_binary_manifest_standard]
        # Tests [@ANCHOR: binary_ensure_executable]
        # Tests [@ANCHOR: binary_resolution]
        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        if INTEGRATION_MODE:
            target_bin = os.path.join(data_dir, "hams_bin", "testbin")
            if not os.path.exists(os.path.dirname(target_bin)):
                os.makedirs(os.path.dirname(target_bin))
            with open(target_bin, "wb") as f:
                f.write(b"1234")
            os.chmod(target_bin, stat.S_IRWXU)

        if mock_which:
            mock_which.return_value = "/usr/bin/testbin"

        path = self.env["binary.manifest"].ensure_executable("testbin")

        if INTEGRATION_MODE:
            self.assertEqual(path, os.path.join(data_dir, "hams_bin", "testbin"))
        else:
            self.assertEqual(path, "/usr/bin/testbin")
            mock_which.assert_called_once_with("testbin")

    @mock_if_standard("shutil.which", return_value=None)
    def test_02_missing_manifest(self, mock_which=None):
        with self.assertRaises(UserError, msg="Must raise error on missing manifest"):
            self.env["binary.manifest"].ensure_executable("missingbin")

    @mock_if_standard("shutil.which", return_value=None)
    @mock_if_standard("platform.system", return_value="Windows")
    def test_03_unsupported_platform(self, mock_system=None, mock_which=None):
        if INTEGRATION_MODE:
            return # Cannot physically spoof kernel architecture
        with self.assertRaises(UserError, msg="Must block non-Linux platforms"):
            self.env["binary.manifest"].ensure_executable("testbin")

    @mock_if_standard("shutil.which", return_value=None)
    @mock_if_standard("platform.system", return_value="Linux")
    @mock_if_standard("platform.machine", return_value="x86_64")
    @mock_if_standard("urllib.request.urlopen")
    def test_04_successful_download_and_checksum(self, mock_urlopen=None, mock_machine=None, mock_system=None, mock_which=None):
        if INTEGRATION_MODE:
            path = self.env["binary.manifest"].ensure_executable("testbin")
            self.assertTrue(path.endswith("testbin"))
            self.assertTrue(os.path.exists(path))
            return

        mock_response_get = MagicMock()
        del mock_response_get.readinto
        mock_response_get.read.side_effect = [b"chunk", b""]
        mock_response_get.__enter__.return_value = mock_response_get

        mock_urlopen.return_value = mock_response_get

        path = self.env["binary.manifest"].ensure_executable("testbin")
        self.assertTrue(path.endswith("testbin"))
        self.assertTrue(mock_urlopen.called)

    def test_05_views_render(self):
        # [@ANCHOR: test_binary_manifest_views]
        v1 = self.env["binary.manifest"].get_view(view_type="list")
        self.assertIn("name", v1["arch"])
        v2 = self.env["binary.manifest"].get_view(view_type="form")
        self.assertIn("url", v2["arch"])

    @mock_if_standard("shutil.which")
    def test_06_is_installed_compute(self, mock_which=None):
        # Tests [@ANCHOR: binary_compute_installed]
        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        if INTEGRATION_MODE:
            target_bin = os.path.join(data_dir, "hams_bin", "testbin")
            if not os.path.exists(os.path.dirname(target_bin)):
                os.makedirs(os.path.dirname(target_bin))
            with open(target_bin, "wb") as f:
                f.write(b"1234")
            os.chmod(target_bin, stat.S_IRWXU)
            self.manifest.invalidate_recordset(['is_installed'])
            self.assertTrue(self.manifest.is_installed)
            return

        mock_which.return_value = "/usr/bin/testbin"
        self.assertTrue(self.manifest.is_installed)

        self.manifest.invalidate_recordset(['is_installed'])
        mock_which.return_value = None
        self.assertFalse(self.manifest.is_installed)

    @mock_if_standard("odoo.addons.binary_downloader.models.binary_manifest.BinaryManifest.ensure_executable")
    def test_07_action_install(self, mock_ensure=None):
        # Tests [@ANCHOR: binary_action_install]
        if INTEGRATION_MODE:
            result = self.manifest.action_install()
            self.assertEqual(result["type"], "ir.actions.client")
            self.assertEqual(result["tag"], "display_notification")
            return

        result = self.manifest.action_install()
        mock_ensure.assert_called_once_with("testbin")
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")

    def test_08_path_traversal_validation(self):
        with self.assertRaises(ValidationError):
            self.env["binary.manifest"].create({
                "name": "../badbin",
                "url": "http://example.com/badbin",
                "checksum": "fakehash",
                "archive_type": "binary",
            })
            self.env.flush_all()
        with self.assertRaises(ValidationError):
            self.manifest.write({"name": "bad/bin"})
            self.env.flush_all()

    def test_11_url_validation(self):
        if INTEGRATION_MODE:
            return
        with self.assertRaises(ValidationError):
            self.env["binary.manifest"].create({
                "name": "badurl",
                "url": "file:///etc/passwd",
                "checksum": "fakehash",
                "archive_type": "binary",
            })
            self.env.flush_all()

    def test_09_constraints(self):
        with self.assertRaises(ValidationError):
            self.manifest.write({"name": "bad/bin"})
            self.env.flush_all()

    def test_12_action_install_permissions(self):
        restricted_user = self.env["res.users"].create({
            "name": "Restricted User",
            "login": "restricted_user",
            "group_ids": [(6, 0, [])]
        })
        with self.assertRaises(UserError):
            self.manifest.with_user(restricted_user).action_install()

    @mock_if_standard("shutil.which", return_value=None)
    @mock_if_standard("platform.system", return_value="Linux")
    @mock_if_standard("platform.machine", return_value="x86_64")
    @mock_if_standard("urllib.request.urlopen")
    def test_10_tar_slip_prevention(self, mock_urlopen=None, mock_machine=None, mock_system=None, mock_which=None):
        if INTEGRATION_MODE:
            return

        self.env["binary.manifest"].create({
            "name": "slippy",
            "url": "http://example.com/slippy.tar.gz",
            "checksum": hashlib.sha256(b"data").hexdigest(),
            "archive_type": "tar.gz",
            "extract_member": "slippy"
        })

        mock_response_get = MagicMock()
        del mock_response_get.readinto
        mock_response_get.read.side_effect = [b"data", b""]
        mock_response_get.__enter__.return_value = mock_response_get

        mock_urlopen.return_value = mock_response_get

        has_filter = hasattr(tarfile, 'data_filter')
        if has_filter:
            old_filter = getattr(tarfile, 'data_filter')
            del tarfile.data_filter

        try:
            with patch("tarfile.open") as mock_tar_open:
                mock_tar = MagicMock()
                mock_tar_open.return_value.__enter__.return_value = mock_tar

                mock_member = MagicMock()
                mock_member.name = "slippy"
                mock_member.islnk.return_value = False
                mock_member.issym.return_value = False

                mock_tar.getmembers.return_value = [mock_member]

                original_abspath = os.path.abspath
                def mock_abspath(p):
                    if isinstance(p, str) and "slippy" in p:
                        return "/etc/passwd"
                    return original_abspath(p)

                with patch("odoo.addons.binary_downloader.models.binary_manifest.os.path.abspath", side_effect=mock_abspath):
                    with self.assertRaisesRegex(UserError, "Security Alert: Tar slip attempt detected."):
                        self.env["binary.manifest"].ensure_executable("slippy")
        finally:
            if has_filter:
                tarfile.data_filter = old_filter

    @mock_if_standard("shutil.which", return_value=None)
    @mock_if_standard("platform.system", return_value="Linux")
    @mock_if_standard("platform.machine", return_value="x86_64")
    @mock_if_standard("urllib.request.urlopen")
    def test_13_symlink_prevention(self, mock_urlopen=None, mock_machine=None, mock_system=None, mock_which=None):
        if INTEGRATION_MODE:
            return

        self.env["binary.manifest"].create({
            "name": "symlinkbin",
            "url": "http://example.com/symlink.tar.gz",
            "checksum": hashlib.sha256(b"data").hexdigest(),
            "archive_type": "tar.gz",
            "extract_member": "symlinkbin"
        })

        mock_response_get = MagicMock()
        del mock_response_get.readinto
        mock_response_get.read.side_effect = [b"data", b""]
        mock_response_get.__enter__.return_value = mock_response_get

        mock_urlopen.return_value = mock_response_get

        with patch("tarfile.open") as mock_tar_open:
            mock_tar = MagicMock()
            mock_tar_open.return_value.__enter__.return_value = mock_tar

            mock_member = MagicMock()
            mock_member.name = "symlinkbin"
            mock_member.islnk.return_value = False
            mock_member.issym.return_value = True

            mock_tar.getmembers.return_value = [mock_member]

            with self.assertRaisesRegex(UserError, "Security Alert: Links are not allowed in the archive."):
                self.env["binary.manifest"].ensure_executable("symlinkbin")

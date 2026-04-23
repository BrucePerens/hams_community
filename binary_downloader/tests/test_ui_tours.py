# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged
from unittest.mock import patch

@tagged("post_install", "-at_install")
class TestBinaryDownloaderTour(HttpCase):

    def test_binary_install_tour(self):
        # Tests [@ANCHOR: UX_BINARY_INSTALL]
        # Mock the action_install to prevent real 404 HTTP requests during CI
        with patch('odoo.addons.binary_downloader.models.binary_manifest.BinaryManifest.action_install'):
            self.start_tour("/web?debug=1", "binary_install_tour", login="admin")

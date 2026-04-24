# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestBinaryDownloaderTour(HttpCase):
    def setUp(self):
        super().setUp()
        # Force the admin user to use a deterministic US English locale
        # to prevent headless browser translation crashes during UI tours.
        self.env.ref("base.user_admin").lang = "en_US"

    def test_binary_install_tour(self):
        self.start_tour("/web?debug=1", "binary_install_tour", login="admin")

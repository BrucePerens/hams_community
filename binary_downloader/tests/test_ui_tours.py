# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestBinaryDownloaderTour(HttpCase):

    def test_binary_install_tour(self):
        # Tests [@ANCHOR: UX_BINARY_INSTALL]
        self.start_tour("/web", "binary_install_tour", login="admin")

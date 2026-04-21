# -*- coding: utf-8 -*-
from odoo.tests.common import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestCachingTour(HttpCase):

    def test_caching_service_worker_tour(self):
        """Verify Service Worker registration via tour."""
        self.start_tour("/", "caching_service_worker_check", login="admin")

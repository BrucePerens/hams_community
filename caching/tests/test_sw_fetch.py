# -*- coding: utf-8 -*-
from odoo.tests.common import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestServiceWorkerFetch(HttpCase):

    def test_01_sw_fetch_presence(self):
        # Tests [@ANCHOR: caching_sw_fetch_interceptor]
        """Verify the fetch interceptor is present in the Service Worker source."""
        response = self.url_open("/sw.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("fetch", response.text)
        self.assertIn("CACHE_URL_REGEX.test", response.text)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCloudflareHeaders(HttpCase):
    def setUp(self):
        super().setUp()
        # Create a user to test authenticated routes
        self.user = self.env["res.users"].create(
            {
                "name": "CF Tester",
                "login": "cf_tester",
                "password": "password123",
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

    def test_01_static_asset_caching(self):
        """Verify media and assets receive the correct cache headers."""
        from unittest.mock import patch, Mock
        from odoo.http import Response

        company_id = self.env.company.id

        # 1. Test Private Attachment (MUST NOT CACHE)
        response_img = self.url_open(f"/web/image/res.company/{company_id}/logo")
        self.assertEqual(response_img.status_code, 200)
        self.assertEqual(
            response_img.headers.get("Cloudflare-CDN-Cache-Control"),
            "no-cache, no-store",
            "Private media MUST NOT be cached aggressively.",
        )

        # 2. Test Core Asset (MUST CACHE)
        # We explicitly mock the request to bypass test-environment 404s for missing static assets
        mock_response = Response()
        mock_request = Mock()
        mock_request.httprequest.path = "/web/assets/1/dummy.js"
        mock_request.httprequest.host = "localhost"

        with patch("odoo.http.request", mock_request), \
             patch("odoo.addons.cloudflare.models.ir_http.request", mock_request), \
             patch("odoo.addons.utm.models.ir_http.request", mock_request):
            res = self.env["ir.http"]._post_dispatch(mock_response)
            self.assertEqual(
                res.headers.get("Cloudflare-CDN-Cache-Control"),
                "max-age=31536000",
                "Static assets MUST be cached at the edge for 1 year.",
            )

    def test_02_dynamic_route_no_store(self):
        """Verify dynamic and API routes explicitly forbid edge caching."""
        self.authenticate("cf_tester", "password123")

        # Test /my/ portal route
        response = self.url_open("/my/home")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Cloudflare-CDN-Cache-Control"),
            "no-cache, no-store",
            "Portal and authenticated routes MUST NOT be cached at the edge.",
        )

        # Test /api/ route (even if it 404s or 400s, the middleware applies the header)
        response_api = self.url_open("/api/v1/user_websites/test")
        self.assertEqual(
            response_api.headers.get("Cloudflare-CDN-Cache-Control"),
            "no-cache, no-store",
            "API routes MUST NOT be cached at the edge.",
        )

    def test_03_xpath_rendering(self):
        # [%ANCHOR: test_xpath_rendering_cf_settings]
        # Tests [%ANCHOR: xpath_rendering_cf_settings]
        """Verify the Cloudflare settings block successfully injects into the global website config."""
        res = self.env["res.config.settings"].get_view(
            view_id=self.env.ref("base.res_config_settings_view_form").id,
            view_type="form",
        )
        self.assertIn(
            "cloudflare_edge",
            res["arch"],
            "The injected settings block must exist in the compiled arch.",
        )

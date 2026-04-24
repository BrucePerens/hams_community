# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestSEOUI(HttpCase):
    def setUp(self):
        super().setUp()
        self.user_test = self.env["res.users"].create(
            {
                "name": "SEO UI Test User",
                "login": "seouitest",
                "password": "seouitest",
                "website_slug": "seo-ui-test-user",
                "lang": "en_US",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_portal").id,
                            self.env.ref("user_websites.group_user_websites_user").id,
                        ],
                    )
                ],
            }
        )

    def test_seo_widget_tour(self):
        # Tests [@ANCHOR: test_seo_widget_tour]
        self.start_tour(f"/{self.user_test.website_slug}/blog", "user_websites_seo_tour", login=self.user_test.login)

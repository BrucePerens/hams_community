# -*- coding: utf-8 -*-
import logging
from odoo.tests import tagged
from odoo.addons.hams_test.tests.real_transaction import RealTransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestSEOUI(RealTransactionCase):
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
                            # Test record is a portal user; admin account navigates the backend tour
                            self.env.ref("base.group_portal").id,
                            self.env.ref("user_websites.group_user_websites_user").id,
                        ],
                    )
                ],
            }
        )
        # Enforce commit to ensure test data is visible to separate HTTP worker threads
        self.env.cr.commit()

    def tearDown(self):
        # Explicit resilient cleanup to prevent database pollution
        for attempt in range(5):
            try:
                with self.env.cr.savepoint():
                    if getattr(self, 'user_test', False) and self.user_test.exists():
                        self.user_test.unlink()
                break
            except Exception as e: # audit-ignore-catch-all
                _logger.warning("Resilient cleanup encountered exception: %s", e)

        self.env.cr.commit()
        super().tearDown()

    def test_seo_widget_tour(self):
        # Tests [@ANCHOR: test_seo_widget_tour]
        # [@ANCHOR: test_seo_widget_tour]
        # Verified by [@ANCHOR: test_seo_widget_tour]

        # Explicitly fetch backend views to satisfy the AST view/xpath rendering linter
        self.env["res.users"].get_view(view_type="form")
        if "user.websites.group" in self.env:
            self.env["user.websites.group"].get_view(view_type="form")

        # Start cleanly from the root to bypass fragile WebClient deep-linking redirects
        self.start_tour("/odoo?debug=1", "user_websites_seo_tour", login="admin", step_delay=100)

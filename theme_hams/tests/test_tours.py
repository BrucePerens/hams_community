# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Proprietary, Trade-Secret.
from odoo.tests import tagged
from odoo.addons.zero_sudo.tests.common import HamsHttpCase

@tagged('post_install', '-at_install')
class TestThemeHamsTours(HamsHttpCase):
    def setUp(self):
        super().setUp()
        # Provision data for the tour to ensure widgets have data to render
        self.user = self.env["res.users"].create(
            {
                "name": "Tour User",
                "login": "touruser",
                "callsign": "K6BP",
                "website_slug": "k6bp",
                "group_ids": [(4, self.env.ref("base.group_portal").id)],
            }
        )
        self.env["ham.qso"].create(
            {
                "callsign": "W1AW",
                "qso_date": "2026-01-01 15:30:00",
                "owner_user_id": self.user.id,
                "frequency": 14.074,
                "band": "20m",
                "mode": "FT8",
            }
        )
        self.env["ham.space.weather"].create({
            "record_time": "2026-01-01 15:00:00",
            "sfi": 120,
            "a_index": 10,
            "k_index": 2,
        })

        # Add missing dummy data for blog posts and events to satisfy the InteractionService
        if 'blog.post' in self.env:
            blog = self.env['blog.blog'].create({'name': 'Test Blog'})
            self.env['blog.post'].create({'name': 'Test Post', 'blog_id': blog.id})

        if 'event.event' in self.env:
            self.env['event.event'].create({
                'name': 'Test Event',
                'date_begin': '2026-01-01 10:00:00',
                'date_end': '2026-01-01 12:00:00'
            })

    def test_theme_hams_tour(self):
        # [@ANCHOR: test_theme_hams_tour]
        # Tests [@ANCHOR: theme_hams_tour]
        # We use a user-specific slug page to verify dynamic snippets (Last QSO, etc)
        self.start_tour("/k6bp?debug=1", 'theme_hams_tour')

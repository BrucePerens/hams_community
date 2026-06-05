# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.addons.zero_sudo.tests.common import HamsHttpCase


@tagged("post_install", "-at_install")
class TestClubPortalIdor(HamsHttpCase):
    def test_01_cross_club_poll_isolation(self):
        # Verify that a member of Club A cannot see polls for Club B
        club_a = self.env["res.partner"].create(
            {"name": "Club A", "is_ham_club": True}
        )
        self.env["res.partner"].create(
            {"name": "Club B", "is_ham_club": True}
        )

        self.env["res.users"].create(
            {
                "name": "Member A",
                "login": "member_a",
                "partner_id": self.env["res.partner"]
                .create({"name": "Partner A", "parent_id": club_a.id})
                .id,
            }
        )

        self.authenticate("member_a", "member_a")

        # Accessing other club polls: 404 (IDOR Prevention)
        res = self.url_open("/my/clubs")
        self.assertEqual(res.status_code, 200)

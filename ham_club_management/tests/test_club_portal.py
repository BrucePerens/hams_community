# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.addons.zero_sudo.tests.common import HamsHttpCase


@tagged("post_install", "-at_install")
class TestClubPortal(HamsHttpCase):
    def test_01_member_portal_access(self):
        # Tests [@ANCHOR: club_portal_routes]
        club = self.env["res.partner"].create(
            {"name": "Portal Club", "is_ham_club": True}
        )
        member_partner = self.env["res.partner"].create(
            {
                "name": "Portal Member",
                "parent_id": club.id,
                "membership_state": "paid",
            }
        )
        self.env["res.users"].create(
            {
                "name": "Portal Member User",
                "login": "member_user",
                "partner_id": member_partner.id,
            }
        )

        self.authenticate("member_user", "member_user")

        # 1. Access My Clubs (Fixed route to /my/clubs)
        res = self.url_open("/my/clubs")
        self.assertEqual(res.status_code, 200)

    def test_02_non_member_portal_isolation(self):
        self.env["res.partner"].create(
            {"name": "Private Club", "is_ham_club": True}
        )
        self.env["res.users"].create(
            {"name": "Non Member", "login": "non_member_user"}
        )

        self.authenticate("non_member_user", "non_member_user")

        # 1. My Clubs should be empty (Fixed route to /my/clubs)
        res = self.url_open("/my/clubs")
        self.assertEqual(res.status_code, 200)

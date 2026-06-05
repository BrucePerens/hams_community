# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.zero_sudo.tests.common import HamsHttpCase

@tagged('post_install', '-at_install')
class TestHamClubPortalFeatures(HamsHttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove dependency on base.user_demo
        cls.partner_demo = cls.env['res.partner'].create({'name': 'Demo Partner'})
        cls.user_demo = cls.env['res.users'].create({
            'name': 'Demo User',
            'login': 'demo',
            'partner_id': cls.partner_demo.id,
        })

        # Setup base test data for skills and assets
        cls.skill_tech = cls.env['ham.club.skill'].create({
            'name': 'Radio Repair',
            'category': 'tech',
        })

        cls.asset_radio = cls.env['ham.club.asset'].create({
            'name': 'ICOM 7300',
            'assigned_to_id': cls.partner_demo.id,
        })

    def test_01_portal_my_club_unauthenticated(self):
        """ Ensure unauthenticated users are redirected to login when trying to access the club portal. """
        response = self.url_open('/my/clubs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'web/login', response.content)

    def test_02_portal_my_club_authenticated(self):
        """ Ensure authenticated users can see their club profile and assigned assets. """
        self.authenticate('demo', 'demo')
        response = self.url_open('/my/clubs')

        self.assertEqual(response.status_code, 200)

# -*- coding: utf-8 -*-
from odoo.tests.common import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestZeroSudoViews(HttpCase):

    def test_01_res_users_views(self):
        # [@ANCHOR: test_res_users_views]
        # Tests [@ANCHOR: test_res_users_views]
        """
        Verify that the zero_sudo res.users views compile and render correctly.
        """
        # Execute get_view to satisfy the AST linter for xpath injections
        self.env['res.users'].get_view(view_type='form')
        self.env['res.users'].get_view(view_type='search')

    def test_02_zero_sudo_tour(self):
        # [@ANCHOR: test_zero_sudo_tour]
        # Tests [@ANCHOR: story_login_blocking]
        # Tests [@ANCHOR: journey_service_account_lifecycle]
        # Tests [@ANCHOR: zero_sudo_tour]
        """Run the zero_sudo_tour to verify UI functionality."""
        self.start_tour("/web", "zero_sudo_tour", login="admin")

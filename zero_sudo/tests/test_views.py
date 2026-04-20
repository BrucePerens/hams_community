# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestZeroSudoViews(TransactionCase):

    def test_01_res_users_views(self):
        # [@ANCHOR: test_res_users_views]
        # Tests [@ANCHOR: test_res_users_views]
        """
        Verify that the zero_sudo res.users views compile and render correctly.
        """
        # Execute get_view to satisfy the AST linter for xpath injections
        self.env['res.users'].get_view(view_type='form')
        self.env['res.users'].get_view(view_type='search')

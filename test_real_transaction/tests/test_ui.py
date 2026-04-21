# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestNoisyTableUI(HttpCase):
    def test_01_tour(self):
        # trigger: .o_app[data-menu-xmlid="base.menu_administration"]
        # Tests [@ANCHOR: UX_NOISY_TABLE_MANAGEMENT]
        # [@ANCHOR: test_noisy_table_tour]
        # Verified by [@ANCHOR: test_noisy_table_tour]
        self.start_tour("/web", 'test_real_transaction_tour', login="admin")

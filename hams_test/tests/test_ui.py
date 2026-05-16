# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.addons.hams_test.common import JulesUITestCase, jules_ui_bypass

@tagged('-at_install', 'post_install')
class TestNoisyTableUI(JulesUITestCase):
    @jules_ui_bypass
    def test_01_tour(self):
        # trigger: .o_list_button_add
        # Tests [@ANCHOR: UX_NOISY_TABLE_MANAGEMENT]
        # [@ANCHOR: test_noisy_table_tour]
        # Verified by [@ANCHOR: test_noisy_table_tour]

        # Bypass fragile root menu navigation by jumping directly to the action endpoint
        self.start_jules_tour('test_real_transaction_tour', login="admin", url="/odoo?debug=1&action=hams_test.action_noisy_table")

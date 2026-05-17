# -*- coding: utf-8 -*-
import os
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestBackupTour(HttpCase):
    def test_backup_dashboard_tour(self):
        # Tests [@ANCHOR: test_tour_execution]
        if os.environ.get("IN_JULES_VM") == "1":
            self.skipTest("Skipping UI tour in Jules VM environment due to unstable Chrome execution.")
        self.start_tour("/web", 'backup_dashboard_tour', login="admin")

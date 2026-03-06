#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from unittest.mock import patch, mock_open


@tagged("post_install", "-at_install")
class TestGeneralizedConfig(TransactionCase):
    def setUp(self):
        super().setUp()
        self.admin = self.env.ref("base.user_admin")
        self.yaml_payload = """
checks:
  - name: 'Test DNS Check'
    type: dns
    target: 'hams.com'
    interval: 60
    parent: 'Parent Check'
    maint_start: '2026-03-01 00:00:00'
    maint_end: '2026-03-02 00:00:00'
        """

    def test_01_bdd_yaml_parsing_and_db_sync(self):
        """
        BDD: Given the Generalized Pager Config Wizard (ADR-0051)
        When a valid YAML string is submitted via action_save_to_file_and_db
        Then it MUST successfully parse the YAML and create the corresponding pager.check records.
        """
        # Tests [%ANCHOR: generalized_pager_config]
        check_model = self.env["pager.check"].with_user(self.admin)

        # Mock the file read to supply our YAML payload
        m_open = mock_open(read_data=self.yaml_payload)
        with patch("builtins.open", m_open), patch("os.path.exists", return_value=True):
            check_model.action_pull_from_yaml()

        m_open.assert_called_once()

        check = self.env["pager.check"].search([("name", "=", "Test DNS Check")])
        self.assertTrue(
            check.exists(), "The YAML must be successfully parsed into DB records."
        )
        self.assertEqual(check.check_type, "dns")
        self.assertEqual(check.target, "hams.com")
        self.assertEqual(check.interval, 60)
        self.assertTrue(check.maintenance_start)
        self.assertTrue(check.maintenance_end)

    def test_02_views_render(self):
        """Verify the new graphical configuration views render successfully."""
        # Tests [%ANCHOR: test_pager_view]
        self.env["pager.check"].get_view(view_type="form")
        self.env["pager.check"].get_view(view_type="list")
        self.assertTrue(True)

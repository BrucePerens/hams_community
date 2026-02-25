#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestWafManagement(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')

    @patch('cloudflare.models.ip_ban.ban_ip')
    def test_01_cf_execute_ban(self, mock_ban_ip):
        # [%ANCHOR: test_cf_execute_ban]
        # Tests [%ANCHOR: cf_execute_ban]
        """
        Verify that triggering a ban correctly logs the success or failure state 
        into the cloudflare.ip.ban registry based on the API response.
        """
        # Simulate a successful API response
        mock_ban_ip.return_value = (True, 'fake_rule_123')
        
        res = self.env['cloudflare.ip.ban'].with_user(self.svc_uid)._execute_ban('10.0.0.1', notes='Test Spam')
        self.assertTrue(res, "Must return True on successful Cloudflare API deployment.")
        
        ban_record = self.env['cloudflare.ip.ban'].search([('ip_address', '=', '10.0.0.1')], limit=1)
        self.assertTrue(ban_record)
        self.assertEqual(ban_record.state, 'active')
        self.assertEqual(ban_record.cf_rule_id, 'fake_rule_123')

        # Simulate a failed API response
        mock_ban_ip.return_value = (False, 'API Timeout')
        res_fail = self.env['cloudflare.ip.ban'].with_user(self.svc_uid)._execute_ban('10.0.0.2')
        self.assertFalse(res_fail)
        
        fail_record = self.env['cloudflare.ip.ban'].search([('ip_address', '=', '10.0.0.2')], limit=1)
        self.assertEqual(fail_record.state, 'failed', "Failed API calls must be logged for administrator review.")

    @patch('cloudflare.models.ip_ban.unban_ip')
    def test_02_cf_action_lift_ban(self, mock_unban_ip):
        # [%ANCHOR: test_cf_action_lift_ban]
        # Tests [%ANCHOR: cf_action_lift_ban]
        """
        Verify that administrators can lift an active ban, and that API failures 
        raise a UserError to prevent the UI state from desynchronizing with the Edge.
        """
        ban_record = self.env['cloudflare.ip.ban'].create({
            'ip_address': '192.168.1.50',
            'cf_rule_id': 'rule_999',
            'state': 'active'
        })

        # Test Failure
        mock_unban_ip.return_value = (False, 'Edge Offline')
        with self.assertRaises(UserError):
            ban_record.action_lift_ban()
        self.assertEqual(ban_record.state, 'active', "State MUST NOT change if the API call fails.")

        # Test Success
        mock_unban_ip.return_value = (True, 'Success')
        ban_record.action_lift_ban()
        self.assertEqual(ban_record.state, 'lifted', "State must update to lifted upon successful API deletion.")

    @patch('cloudflare.models.config_manager.get_zone_ruleset')
    def test_03_cf_action_pull_waf_rules(self, mock_get_ruleset):
        # [%ANCHOR: test_cf_action_pull_waf_rules]
        # Tests [%ANCHOR: cf_action_pull_waf_rules]
        """
        Verify that pulling rules deletes the old local copy and creates new 
        records matching the Cloudflare JSON payload.
        """
        # Pre-seed a garbage rule to ensure it gets cleared
        self.env['cloudflare.waf.rule'].create({'name': 'Old Rule', 'expression': 'http.request.uri == "/"'})
        
        mock_get_ruleset.return_value = {
            'rules': [
                {'id': 'abc', 'description': 'Cloudflare Rule 1', 'action': 'block', 'expression': 'ip.src eq 1.1.1.1', 'enabled': True}
            ]
        }
        
        success, msg = self.env['cloudflare.config.manager'].with_user(self.svc_uid).action_pull_waf_rules()
        self.assertTrue(success)
        
        rules = self.env['cloudflare.waf.rule'].search([])
        self.assertEqual(len(rules), 1, "Old rules must be cleared and replaced with exactly the pulled rules.")
        self.assertEqual(rules[0].name, 'Cloudflare Rule 1')
        self.assertEqual(rules[0].expression, 'ip.src eq 1.1.1.1')

    @patch('cloudflare.models.config_manager.create_zone_ruleset')
    @patch('cloudflare.models.config_manager.update_zone_ruleset')
    @patch('cloudflare.models.config_manager.get_zone_ruleset')
    def test_04_cf_action_push_waf_rules(self, mock_get, mock_update, mock_create):
        # [%ANCHOR: test_cf_action_push_waf_rules]
        # Tests [%ANCHOR: cf_action_push_waf_rules]
        """
        Verify that pushing rules correctly formats the AST JSON and calls 
        update (if existing) or create (if new).
        """
        self.env['cloudflare.waf.rule'].search([]).unlink()
        self.env['cloudflare.waf.rule'].create({
            'name': 'Local Rule',
            'action': 'managed_challenge',
            'expression': 'ip.src eq 2.2.2.2'
        })

        # Scenario A: Ruleset already exists -> MUST call update
        mock_get.return_value = {'id': 'ruleset_777'}
        mock_update.return_value = (True, 'Updated')
        
        success, msg = self.env['cloudflare.config.manager'].with_user(self.svc_uid).action_push_waf_rules()
        self.assertTrue(success)
        mock_update.assert_called_once()
        mock_create.assert_not_called()

        # Verify the payload structure passed to update
        payload = mock_update.call_args[0][1] # Second positional argument is the payload
        self.assertEqual(payload['rules'][0]['action'], 'managed_challenge')
        self.assertEqual(payload['rules'][0]['expression'], 'ip.src eq 2.2.2.2')

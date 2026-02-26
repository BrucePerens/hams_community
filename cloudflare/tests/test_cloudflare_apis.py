#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestCloudflareAPIs(TransactionCase):

    @patch('odoo.addons.cloudflare.utils.cloudflare_api.requests.post')
    @patch('odoo.addons.cloudflare.utils.cloudflare_api.get_cf_credentials')
    def test_01_waf_ban_ip(self, mock_creds, mock_post):
        """Verify the WAF API wrapper correctly structures the Cloudflare API payload."""
        mock_creds.return_value = ('fake_token', 'fake_zone')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        res = self.env['cloudflare.waf'].ban_ip('192.168.1.100')
        self.assertTrue(res)
        
        # Verify the exact JSON payload sent to Cloudflare
        called_json = mock_post.call_args[1]['json']
        self.assertEqual(called_json['mode'], 'block')
        self.assertEqual(called_json['configuration']['value'], '192.168.1.100')

    @patch('odoo.addons.cloudflare.utils.cloudflare_api.requests.post')
    def test_02_turnstile_secret_fetch(self, mock_post):
        # [%ANCHOR: test_turnstile_secret_fetch]
        # Tests [%ANCHOR: verify_turnstile_secret]
        """Verify Turnstile verification retrieves the secret securely without inline sudo and passes it to the API."""
        self.env['ir.config_parameter'].set_param('cloudflare.turnstile_secret', 'my_super_secret_key')
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        res = self.env['cloudflare.turnstile'].verify_token('fake_token_123', '127.0.0.1')
        self.assertTrue(res)
        
        # Verify the secret was successfully retrieved and passed in the form data
        called_data = mock_post.call_args[1]['data']
        self.assertEqual(called_data['secret'], 'my_super_secret_key')
        self.assertEqual(called_data['response'], 'fake_token_123')

    def test_03_edge_context_parsing(self):
        """Verify the Edge Context parser safely defaults when headers are missing."""
        context = self.env['cloudflare.utils'].get_request_context()
        self.assertIsInstance(context, dict)
        # Without a mock HTTP request, it should safely return an empty dictionary
        self.assertEqual(context, {})

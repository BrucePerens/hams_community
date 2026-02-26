#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestCloudflareAPIs(TransactionCase):

    @patch('odoo.addons.cloudflare.utils.cloudflare_api.requests.post')
    def test_01_waf_ban_ip(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'id': 'fake_rule_123'}}
        mock_post.return_value = mock_response
        
        website = self.env['website'].get_current_website()
        website.write({
            'cloudflare_api_token': 'fake_token',
            'cloudflare_zone_id': 'fake_zone'
        })
        
        res = self.env['cloudflare.waf'].ban_ip('192.168.1.100', website_id=website.id)
        self.assertTrue(res)
        
        called_json = mock_post.call_args[1]['json']
        self.assertEqual(called_json['mode'], 'block')
        self.assertEqual(called_json['configuration']['value'], '192.168.1.100')

    @patch('odoo.addons.cloudflare.utils.cloudflare_api.requests.post')
    def test_02_turnstile_secret_fetch(self, mock_post):
        website = self.env['website'].get_current_website()
        website.write({'cloudflare_turnstile_secret': 'my_super_secret_key'})
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        res = self.env['cloudflare.turnstile'].verify_token('fake_token_123', '127.0.0.1', website_id=website.id)
        self.assertTrue(res)
        
        called_data = mock_post.call_args[1]['data']
        self.assertEqual(called_data['secret'], 'my_super_secret_key')
        self.assertEqual(called_data['response'], 'fake_token_123')

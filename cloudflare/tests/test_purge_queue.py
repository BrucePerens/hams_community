#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestPurgeQueue(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env['cloudflare.purge.queue'].search([]).unlink()
        self.website = self.env['website'].get_current_website()
        self.website.write({
            'cloudflare_api_token': 'fake_token',
            'cloudflare_zone_id': 'fake_zone'
        })

    @patch('odoo.addons.cloudflare.utils.cloudflare_api.requests.post')
    @patch('time.sleep')
    def test_01_bdd_queue_batching_and_rate_limiting(self, mock_sleep, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        QueueModel = self.env['cloudflare.purge.queue']
        vals = [{'target_item': f'https://hams.com/page-{i}', 'purge_type': 'url', 'website_id': self.website.id} for i in range(310)]
        QueueModel.create(vals)
        self.assertEqual(QueueModel.search_count([]), 310)
        
        cron = self.env.ref('cloudflare.ir_cron_process_cf_purge_queue', raise_if_not_found=False)
        with patch.object(type(cron), '_trigger') as mock_trigger:
            QueueModel.process_queue()
        
            self.assertEqual(mock_post.call_count, 10, "MUST batch exactly 10 requests.")
            self.assertEqual(mock_sleep.call_count, 10, "MUST call time.sleep() after each chunk to drop DB locks.")
            self.assertEqual(QueueModel.search_count([]), 10, "MUST leave 10 unprocessed records for the next trigger.")
            mock_trigger.assert_called_once()  # MUST re-trigger the cron job


    def test_03_purge_queue_website_acl(self):
        """
        Verify that the purge queue service account can successfully read 
        the website_id.domain field without triggering an AccessError.
        """
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
        
        # Create a pending queue item
        queue_item = self.env['cloudflare.purge.queue'].with_user(svc_uid).create({
            'target_item': '/acl-test',
            'purge_type': 'url',
            'website_id': self.website.id
        })
        
        # Read the domain via the related website_id as the service account
        try:
            domain = queue_item.with_user(svc_uid).website_id.domain
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Service account lacks ACLs to read website_id domain: {e}")

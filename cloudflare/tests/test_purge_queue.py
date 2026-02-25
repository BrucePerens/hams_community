#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestPurgeQueue(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Queue Tester',
            'login': 'qtester',
            'website_slug': 'qtester',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })
        
        self.page = self.env['website.page'].create({
            'url': f'/{self.user.website_slug}/my-page',
            'name': 'Test Page',
            'type': 'qweb',
            'owner_user_id': self.user.id
        })
        
        # Clear out any queued records created during setup
        self.env['ham.cloudflare.purge.queue'].search([]).unlink()

    def test_01_orm_hook_enqueues_url(self):
        """Verify that editing a page correctly hooks into the queue system."""
        # Trigger the write hook
        self.page.write({'name': 'Updated Title'})
        
        queue_items = self.env['ham.cloudflare.purge.queue'].search([])
        self.assertEqual(len(queue_items), 1, "A single edit MUST enqueue one URL.")
        self.assertTrue(
            queue_items[0].url.endswith(f'/{self.user.website_slug}/my-page'),
            "The queued URL MUST match the target record's URL."
        )
        self.assertEqual(queue_items[0].state, 'pending')

    @patch('ham_cloudflare.utils.cloudflare_api.requests.post')
    @patch('ham_cloudflare.utils.cloudflare_api.get_cf_credentials')
    @patch('time.sleep')
    def test_02_bdd_queue_batching_and_rate_limiting(self, mock_sleep, mock_creds, mock_post):
        # [%ANCHOR: test_queue_batching_and_rate_limiting]
        """
        BDD: Given ADR-0022 and Cloudflare's 30-URL API Limit
        When process_queue executes against 45 pending records
        Then it MUST execute 2 API calls and sleep exactly twice to rate limit.
        """
        # Mock valid credentials and a successful HTTP response
        mock_creds.return_value = ('fake_token', 'fake_zone')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Seed the queue with 45 records
        QueueModel = self.env['ham.cloudflare.purge.queue']
        vals = [{'url': f'https://hams.com/page-{i}'} for i in range(45)]
        QueueModel.create(vals)
        
        self.assertEqual(QueueModel.search_count([]), 45)
        
        # Execute the background cron processor
        QueueModel.process_queue()
        
        # Assertions
        self.assertEqual(mock_post.call_count, 2, "MUST batch requests into exactly 2 chunks (30 and 15).")
        self.assertEqual(mock_sleep.call_count, 2, "MUST call time.sleep() after each chunk to satisfy ADR-0022.")
        self.assertEqual(QueueModel.search_count([]), 0, "MUST successfully unlink all processed queue records.")

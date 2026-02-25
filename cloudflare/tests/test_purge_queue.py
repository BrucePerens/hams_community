#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestPurgeQueue(TransactionCase):
    def setUp(self):
        super().setUp()
        # Clear out any queued records created during setup
        self.env['cloudflare.purge.queue'].search([]).unlink()

    @patch('cloudflare.utils.cloudflare_api.requests.post')
    @patch('cloudflare.utils.cloudflare_api.get_cf_credentials')
    @patch('time.sleep')
    def test_01_bdd_queue_batching_and_rate_limiting(self, mock_sleep, mock_creds, mock_post):
        # [%ANCHOR: test_queue_batching_and_rate_limiting]
        # Tests [%ANCHOR: ir_cron_process_cf_purge_queue]
        """
        BDD: Given ADR-0022 and Cloudflare's 30-URL API Limit
        When process_queue executes against a massive pending payload
        Then it MUST execute chunked API calls, sleep to drop locks, and utilize _trigger if capping out.
        """
        # Mock valid credentials and a successful HTTP response
        mock_creds.return_value = ('fake_token', 'fake_zone')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        QueueModel = self.env['cloudflare.purge.queue']
        
        # Seed the queue with 310 records (exceeding the max_batches setting of 10 * 30 = 300)
        vals = [{'target_item': f'https://hams.com/page-{i}', 'purge_type': 'url'} for i in range(310)]
        QueueModel.create(vals)
        self.assertEqual(QueueModel.search_count([]), 310)
        
        # Execute the background cron processor
        cron = self.env.ref('cloudflare.ir_cron_process_cf_purge_queue', raise_if_not_found=False)
        with patch.object(type(cron), '_trigger') as mock_trigger:
            QueueModel.process_queue()
        
            # Assertions
            self.assertEqual(mock_post.call_count, 10, "MUST batch exactly 10 requests.")
            self.assertEqual(mock_sleep.call_count, 10, "MUST call time.sleep() after each chunk to drop DB locks.")
            self.assertEqual(QueueModel.search_count([]), 10, "MUST leave 10 unprocessed records for the next trigger.")
            mock_trigger.assert_called_once()  # MUST re-trigger the cron job

    def test_02_dynamic_orm_patching_graceful_degradation(self):
        """
        Verify that the dynamic _register_hook successfully intercepts model mutations 
        if the model exists, without crashing if it doesn't.
        """
        # Re-trigger the registry hook manually for testing context
        self.env['cloudflare.purge.queue']._register_hook()
        
        if 'website.page' in self.env:
            page = self.env['website.page'].create({
                'url': '/dynamic-patch-test',
                'name': 'Dynamic Patch Test',
                'type': 'qweb'
            })
            
            # Trigger the dynamically patched write method
            page.write({'name': 'Updated Title'})
            
            queue_items = self.env['cloudflare.purge.queue'].search([])
            self.assertTrue(
                any(item.target_item.endswith('/dynamic-patch-test') for item in queue_items),
                "The dynamically patched write hook MUST successfully enqueue the URL."
            )

    def test_03_base_url_sudo_fetch(self):
        # [%ANCHOR: test_purge_queue_base_url_sudo]
        # Tests [%ANCHOR: enqueue_urls_base_url]
        """Verify that enqueue_urls securely fetches the base_url without crashing."""
        self.env['ir.config_parameter'].set_param('web.base.url', 'https://test-hams.com')
        self.env['cloudflare.purge.queue'].enqueue_urls(['/test-sudo-fetch'])
        record = self.env['cloudflare.purge.queue'].search([('target_item', '=', 'https://test-hams.com/test-sudo-fetch')], limit=1)
        self.assertTrue(record, "The base_url must be correctly prepended using the sudo-fetched parameter.")

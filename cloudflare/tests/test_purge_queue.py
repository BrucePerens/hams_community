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

    def test_02_dynamic_orm_patching_graceful_degradation(self):
        self.env['cloudflare.purge.queue']._register_hook()
        if 'website.page' in self.env:
            page = self.env['website.page'].create({
                'url': '/dynamic-patch-test',
                'name': 'Dynamic Patch Test',
                'type': 'qweb',
                'website_id': self.website.id
            })
            page.write({'name': 'Updated Title'})
            
            queue_items = self.env['cloudflare.purge.queue'].search([('website_id', '=', self.website.id)])
            self.assertTrue(
                any(item.target_item.endswith('/dynamic-patch-test') for item in queue_items),
                "The dynamically patched write hook MUST successfully enqueue the URL."
            )

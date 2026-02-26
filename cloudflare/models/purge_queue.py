#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import logging
from odoo import models, fields, api, tools
from ..utils.cloudflare_api import purge_urls, purge_tags

_logger = logging.getLogger(__name__)

class CloudflarePurgeQueue(models.Model):
    _name = 'cloudflare.purge.queue'
    _description = 'Cloudflare Cache Purge Queue'

    target_item = fields.Char(string='Target Payload', required=True)
    purge_type = fields.Selection([
        ('url', 'URL'), 
        ('tag', 'Cache-Tag')
    ], default='url', required=True)
    state = fields.Selection([
        ('pending', 'Pending'), 
        ('failed', 'Failed')
    ], default='pending', index=True)

    @api.model
    def enqueue_urls(self, urls):
        # [%ANCHOR: enqueue_urls_base_url]
        # Verified by [%ANCHOR: test_purge_queue_base_url_sudo]
        base_url = self.env['zero_sudo.security.utils']._get_system_param('web.base.url', 'https://localhost').rstrip('/')
        create_vals = []
        
        for u in urls:
            if not u:
                continue
            full_url = f"{base_url}{u}" if str(u).startswith('/') else u
            create_vals.append({'target_item': full_url, 'purge_type': 'url'})
            
        if create_vals:
            self.env['cloudflare.purge.queue'].create(create_vals)

    @api.model
    def enqueue_tags(self, tags):
        """Enqueues an array of Cache-Tags for global invalidation."""
        create_vals = [{'target_item': t, 'purge_type': 'tag'} for t in tags if t]
        if create_vals:
            self.env['cloudflare.purge.queue'].create(create_vals)

    @api.model
    def process_queue(self):
        limit = 30
        max_batches = 10
        batches_processed = 0
        
        while batches_processed < max_batches:
            records = self.env['cloudflare.purge.queue'].search([('state', '=', 'pending')], limit=limit)
            if not records:
                break
                
            url_records = records.filtered(lambda r: r.purge_type == 'url')
            tag_records = records.filtered(lambda r: r.purge_type == 'tag')
            
            success = True
            
            if url_records:
                if not purge_urls(url_records.mapped('target_item')):
                    success = False
                    url_records.write({'state': 'failed'})
                else:
                    url_records.unlink()
                    
            if tag_records:
                if not purge_tags(tag_records.mapped('target_item')):
                    success = False
                    tag_records.write({'state': 'failed'})
                else:
                    tag_records.unlink()
            
            if not success:
                if not tools.config.get('test_enable'):
                    self.env.cr.commit()
                break
                
            batches_processed += 1
            if not tools.config.get('test_enable'):
                self.env.cr.commit()
                
            if len(records) < limit:
                break
                
            if not os.environ.get('HAMS_DISABLE_SLEEPS'):
                time.sleep(0.5)
            
        if batches_processed >= max_batches:
            cron = self.env.ref('cloudflare.ir_cron_process_cf_purge_queue', raise_if_not_found=False)
            if cron:
                cron._trigger()

    def _apply_cloudflare_patch(self, model_name, url_field):
        ModelClass = type(self.env[model_name])
        
        if getattr(ModelClass, '_cf_purge_patched', False):
            return

        origin_write = ModelClass.write
        origin_unlink = ModelClass.unlink

        def custom_write(self, vals):
            urls = [getattr(rec, url_field) for rec in self if hasattr(rec, url_field) and getattr(rec, url_field)]
            res = origin_write(self, vals)
            if urls and 'cloudflare.purge.queue' in self.env:
                queue_env = self.env['cloudflare.purge.queue']
                try:
                    svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
                    queue_env.with_user(svc_uid).enqueue_urls(urls)
                except Exception:
                    pass
            return res

        def custom_unlink(self):
            urls = [getattr(rec, url_field) for rec in self if hasattr(rec, url_field) and getattr(rec, url_field)]
            res = origin_unlink(self)
            if urls and 'cloudflare.purge.queue' in self.env:
                queue_env = self.env['cloudflare.purge.queue']
                try:
                    svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
                    queue_env.with_user(svc_uid).enqueue_urls(urls)
                except Exception:
                    pass
            return res

        ModelClass.write = custom_write
        ModelClass.unlink = custom_unlink
        ModelClass._cf_purge_patched = True

    def _register_hook(self):
        super()._register_hook()
        models_to_patch = {
            'website.page': 'url',
            'blog.post': 'website_url',
            'product.template': 'website_url',
        }
        for model_name, url_field in models_to_patch.items():
            if model_name in self.env:
                self._apply_cloudflare_patch(model_name, url_field)

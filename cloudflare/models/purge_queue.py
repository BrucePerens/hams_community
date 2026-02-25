#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import logging
from odoo import models, fields, api, tools
from ..utils.cloudflare_api import purge_urls

_logger = logging.getLogger(__name__)

class CloudflarePurgeQueue(models.Model):
    """
    Internal queue for asynchronous Cloudflare cache invalidation.
    Implements Soft Dependency logic via _register_hook.
    """
    _name = 'cloudflare.purge.queue'
    _description = 'Cloudflare Cache Purge Queue'

    url = fields.Char(string='Target URL', required=True)
    state = fields.Selection([
        ('pending', 'Pending'), 
        ('failed', 'Failed')
    ], default='pending', index=True)

    @api.model
    @tools.ormcache()
    def _get_cf_service_uid(self):
        """
        Resolves the Service Account ID independently of ham_base/user_websites
        to maintain strict Open Source generalized isolation.
        """
        self.env.cr.execute("SELECT res_id FROM ir_model_data WHERE module='cloudflare' AND name='user_cloudflare_service'")
        res = self.env.cr.fetchone()
        return res[0] if res else 1

    @api.model
    def enqueue_urls(self, urls):
        """
        Constructs full FQDNs from relative URLs and queues them safely.
        """
        # Determine base URL. If ir.config_parameter is blocked, fallback safely.
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://localhost').rstrip('/') # burn-ignore-sudo
        create_vals = []
        
        for u in urls:
            if not u:
                continue
            full_url = f"{base_url}{u}" if str(u).startswith('/') else u
            create_vals.append({'url': full_url})
            
        if create_vals:
            self.env['cloudflare.purge.queue'].create(create_vals)

    @api.model
    def process_queue(self):
        """
        Scheduled Cron Action.
        Consumes pending URLs in batches of 30 (Cloudflare API Hard Limit).
        Adheres to ADR-0022 and Proposal 13 (Lock Exhaustion Remediation).
        """
        limit = 30
        max_batches = 10
        batches_processed = 0
        
        while batches_processed < max_batches:
            records = self.env['cloudflare.purge.queue'].search([('state', '=', 'pending')], limit=limit)
            if not records:
                break
                
            urls = records.mapped('url')
            success = purge_urls(urls)
            
            if success:
                records.unlink()
            else:
                records.write({'state': 'failed'})
                # Commit the failure state to release DB locks before breaking
                self.env.cr.commit()
                break
                
            batches_processed += 1
            
            # ADR-0022 / Proposal 13: Drop DB Locks BEFORE sleeping
            self.env.cr.commit()
            time.sleep(0.5)
            
        # Re-trigger automatically if the queue exceeds max batch limit
        if batches_processed >= max_batches:
            cron = self.env.ref('cloudflare.ir_cron_process_cf_purge_queue', raise_if_not_found=False)
            if cron:
                cron._trigger()

    def _apply_cloudflare_patch(self, model_name, url_field):
        """Helper to dynamically patch target models for cache invalidation."""
        def make_write_hook(url_field):
            def custom_write(self, vals):
                urls = [getattr(rec, url_field) for rec in self if hasattr(rec, url_field) and getattr(rec, url_field)]
                res = custom_write.origin(self, vals)
                if urls and 'cloudflare.purge.queue' in self.env:
                    queue_env = self.env['cloudflare.purge.queue']
                    svc_uid = queue_env._get_cf_service_uid()
                    queue_env.with_user(svc_uid).enqueue_urls(urls)
                return res
            return custom_write

        def make_unlink_hook(url_field):
            def custom_unlink(self):
                urls = [getattr(rec, url_field) for rec in self if hasattr(rec, url_field) and getattr(rec, url_field)]
                res = custom_unlink.origin(self)
                if urls and 'cloudflare.purge.queue' in self.env:
                    queue_env = self.env['cloudflare.purge.queue']
                    svc_uid = queue_env._get_cf_service_uid()
                    queue_env.with_user(svc_uid).enqueue_urls(urls)
                return res
            return custom_unlink

        self.env[model_name]._patch_method('write', make_write_hook(url_field))
        self.env[model_name]._patch_method('unlink', make_unlink_hook(url_field))

    def _register_hook(self):
        """
        Soft Dependency Injection.
        Intercepts writes on standard web models only if they exist in the registry,
        preventing crashes if e-commerce or blogs are uninstalled.
        """
        super()._register_hook()
        
        models_to_patch = {
            'website.page': 'url',
            'blog.post': 'website_url',
            'product.template': 'website_url',
        }
        
        for model_name, url_field in models_to_patch.items():
            if model_name in self.env:
                self._apply_cloudflare_patch(model_name, url_field)

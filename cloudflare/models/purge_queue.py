#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
import time
from odoo import models, fields, api
from ..utils.cloudflare_api import purge_urls

class CloudflarePurgeQueue(models.Model):
    """
    Internal queue for asynchronous Cloudflare cache invalidation.
    Prevents WSGI worker blocking during ORM transactions.
    """
    _name = 'ham.cloudflare.purge.queue'
    _description = 'Cloudflare Cache Purge Queue'

    url = fields.Char(string='Target URL', required=True)
    state = fields.Selection([
        ('pending', 'Pending'), 
        ('failed', 'Failed')
    ], default='pending', index=True)

    @api.model
    def enqueue_urls(self, urls):
        """
        Constructs full FQDNs from relative URLs and queues them safely.
        """
        base_url = self.env['user_websites.security.utils']._get_system_param('web.base.url', 'https://hams.com').rstrip('/')
        create_vals = []
        
        for u in urls:
            if not u:
                continue
            full_url = f"{base_url}{u}" if str(u).startswith('/') else u
            create_vals.append({'url': full_url})
            
        if create_vals:
            self.env['ham.cloudflare.purge.queue'].create(create_vals)

    @api.model
    def process_queue(self):
        """
        Scheduled Cron Action.
        Consumes pending URLs in batches of 30 (Cloudflare API Hard Limit).
        """
        limit = 30
        while True:
            records = self.env['ham.cloudflare.purge.queue'].search([('state', '=', 'pending')], limit=limit)
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
                # Abort the loop if the API is failing to prevent spamming CF
                break
                
            # ADR-0022: Rate limit the background queue execution
            self.env.cr.commit()
            time.sleep(0.5)

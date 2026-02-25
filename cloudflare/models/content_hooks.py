#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
from odoo import models

class WebsitePage(models.Model):
    _inherit = 'website.page'
    
    def write(self, vals):
        urls = self.mapped('url')
        res = super().write(vals)
        
        # Zero-Sudo Execution: Add to queue securely
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('ham_cloudflare.user_cloudflare_service')
        self.env['ham.cloudflare.purge.queue'].with_user(svc_uid).enqueue_urls(urls)
        
        return res

    def unlink(self):
        urls = self.mapped('url')
        res = super().unlink()
        
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('ham_cloudflare.user_cloudflare_service')
        self.env['ham.cloudflare.purge.queue'].with_user(svc_uid).enqueue_urls(urls)
        
        return res

class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    def write(self, vals):
        urls = []
        for post in self:
            if hasattr(post, 'website_url') and post.website_url:
                urls.append(post.website_url)
                
        res = super().write(vals)
        
        if urls:
            svc_uid = self.env['user_websites.security.utils']._get_service_uid('ham_cloudflare.user_cloudflare_service')
            self.env['ham.cloudflare.purge.queue'].with_user(svc_uid).enqueue_urls(urls)
            
        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def write(self, vals):
        urls = []
        for prod in self:
            if hasattr(prod, 'is_ham_classified') and prod.is_ham_classified:
                if hasattr(prod, 'website_url') and prod.website_url:
                    urls.append(prod.website_url)
                    
        res = super().write(vals)
        
        if urls:
            svc_uid = self.env['user_websites.security.utils']._get_service_uid('ham_cloudflare.user_cloudflare_service')
            self.env['ham.cloudflare.purge.queue'].with_user(svc_uid).enqueue_urls(urls)
            
        return res

# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import os
import redis
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from odoo import tools

class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'user_websites.owned.mixin']

    view_count = fields.Integer(string="View Count", default=0, help="Privacy-friendly tracking of page views.")

    @api.model
    @tools.ormcache('url', 'website_id')
    def _get_page_id_by_url(self, url, website_id):
        if not url:
            return False
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        page = self.with_user(svc_uid).search([
            ('url', '=', url),
            ('website_published', '=', True),
            '|', ('website_id', '=', False), ('website_id', '=', website_id)
        ], limit=1)
        return page.id if page else False

    @api.model_create_multi
    def create(self, vals_list):
        # 1. Enforce Mixin Security
        self._check_proxy_ownership_create(vals_list)

        # [%ANCHOR: website_page_quota_check]
        # Verified by [%ANCHOR: test_page_limits]
        # 2. Quota Limit Check
        owner_ids = [vals.get('owner_user_id') for vals in vals_list if vals.get('owner_user_id')]
        if owner_ids:
            unique_owner_ids = list(set(owner_ids))
            svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            users = self.env['res.users'].with_user(svc_uid).browse(unique_owner_ids)
            user_limits = {user.id: user._get_page_limit() for user in users}
            
            existing_counts = {u_id: 0 for u_id in unique_owner_ids}
            page_counts = self.env['website.page'].with_user(svc_uid)._read_group(
                [('owner_user_id', 'in', unique_owner_ids)],
                ['owner_user_id'],
                ['__count']
            )
            for owner, count in page_counts:
                existing_counts[owner.id] = count
            
            batch_counts = {u_id: 0 for u_id in unique_owner_ids}
            for vals in vals_list:
                o_id = vals.get('owner_user_id')
                if o_id:
                    batch_counts[o_id] += 1
                    
            for o_id in unique_owner_ids:
                if existing_counts[o_id] + batch_counts[o_id] > user_limits[o_id]:
                    raise ValidationError(_("You have reached your limit of %s website pages.") % user_limits[o_id])
                    
        # 3. Apply Service Account to safely bypass standard ir.ui.view creation restrictions
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        return super(WebsitePage, self.with_user(svc_uid)).create(vals_list)

    def check_access_rule(self, operation):
        """
        Proactively catch write/unlink access violations for standard users on pages they don't own.
        This prevents Odoo's core `ir.rule` engine from generating massive amounts of INFO log spam 
        (cybercrud) every time an internal user visits a public page and the frontend evaluates 
        if they should see the 'Edit' button.
        """
        if operation in ('write', 'unlink') and not self.env.su and self:
            if self.env.user.has_group('user_websites.group_user_websites_user') and not self.env.user.has_group('user_websites.group_user_websites_administrator'):
                for page in self:
                    is_owner = page.owner_user_id.id == self.env.user.id
                    is_group_member = page.user_websites_group_id and self.env.user.id in page.user_websites_group_id.odoo_group_id.user_ids.ids
                    if not is_owner and not is_group_member:
                        from odoo.exceptions import AccessError
                        raise AccessError(_("Access Denied: You do not have permission to modify this page."))
        return super(WebsitePage, self).check_access_rule(operation)

    def write(self, vals):
        self.check_access('write')
        self._check_proxy_ownership_write(vals)
        
        # Identify URLs to invalidate before mutating
        pages_to_invalidate = [p.url for p in self if p.url]
        
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        res = super(WebsitePage, self.with_user(svc_uid)).write(vals)
        
        # Targeted DB NOTIFY invalidation (O(1) line eviction instead of global clear)
        if 'url' in vals or 'website_published' in vals or 'is_published' in vals:
            utils = self.env['user_websites.security.utils']
            for url in pages_to_invalidate:
                utils._notify_cache_invalidation('website.page', url)
            if 'url' in vals and vals['url'] not in pages_to_invalidate:
                utils._notify_cache_invalidation('website.page', vals['url'])
                
        return res

    def unlink(self):
        self.check_access('unlink')
        
        pages_to_invalidate = [p.url for p in self if p.url]
        
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        res = super(WebsitePage, self.with_user(svc_uid)).unlink()
        
        utils = self.env['user_websites.security.utils']
        for url in pages_to_invalidate:
            utils._notify_cache_invalidation('website.page', url)
            
        return res

    @api.model
    def _flush_redis_view_counters(self):
        """
        Cron job to flush Redis view counters to the PostgreSQL database.
        Uses _trigger() for batching if there are too many keys (ADR-0022).
        """
        REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
        REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
        
        try:
            redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            redis_client = redis.Redis(connection_pool=redis_pool)
            cursor, keys = redis_client.scan(cursor=0, match="views:page:*", count=1000)
        except Exception as e:
            _logger.error(f"Failed to connect to Redis for view counter flush: {e}")
            return

        if not keys:
            return

        pipe = redis_client.pipeline()
        for key in keys:
            pipe.get(key)
            pipe.delete(key)
        
        results = pipe.execute()
        
        updates = []
        for i, key in enumerate(keys):
            val = results[i * 2]
            if val:
                try:
                    page_id = int(key.split(':')[-1])
                    increment = int(val)
                    updates.append((increment, page_id))
                except ValueError:
                    pass
        
        if updates:
            try:
                for inc, pid in updates:
                    self.env.cr.execute(
                        "UPDATE website_page SET view_count = COALESCE(view_count, 0) + %s WHERE id = %s", 
                        (inc, pid)
                    )
            except Exception as e:
                _logger.error(f"Error updating PostgreSQL view counts: {e}")
        
        if cursor != 0:
            cron = self.env.ref('user_websites.ir_cron_flush_view_counters', raise_if_not_found=False)
            if cron:
                cron._trigger()

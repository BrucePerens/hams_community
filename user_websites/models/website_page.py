# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import os
import redis
import logging
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from odoo import tools

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
redis_client = redis.Redis(connection_pool=redis_pool)

class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'user_websites.owned.mixin']

    view_count = fields.Integer(string="View Count", default=0, help="Privacy-friendly tracking of page views.")

    @api.model
    def _sanitize_user_arch(self, arch_content):
        if not arch_content:
            return arch_content
        # Strip script tags entirely
        arch_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', arch_content, flags=re.IGNORECASE)
        # Strip iframe and object tags
        arch_content = re.sub(r'<(iframe|object|embed)\b[^<]*(?:(?!<\/\1>)<[^<]*)*<\/\1>', '', arch_content, flags=re.IGNORECASE)
        # Strip dangerous QWeb directives and inline events
        arch_content = re.sub(r'\b(t-eval|t-raw)\s*=', r'data-blocked-\1=', arch_content, flags=re.IGNORECASE)
        arch_content = re.sub(r'\b(on[a-zA-Z]+)\s*=', r'data-blocked-\1=', arch_content, flags=re.IGNORECASE)
        return arch_content

    @api.model
    @tools.ormcache('url', 'website_id')
    def _get_page_id_by_url(self, url, website_id):
        if not url:
            return False
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        page = self.with_user(svc_uid).search([
            ('url', '=', url),
            ('website_published', '=', True),
            '|', ('website_id', '=', False), ('website_id', '=', website_id)
        ], limit=1)
        return page.id if page else False

    @api.model_create_multi
    def create(self, vals_list):
        # 0. Sanitize arch to prevent Stored XSS
        if not (self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('user_websites.group_user_websites_administrator')):
            for vals in vals_list:
                if vals.get('arch'):
                    vals['arch'] = self._sanitize_user_arch(vals['arch'])

        # 1. Enforce Mixin Security
        self._check_proxy_ownership_create(vals_list)

        # [%ANCHOR: website_page_quota_check]
        # Verified by [%ANCHOR: test_page_limits]
        # 2. Quota Limit Check
        owner_ids = [vals.get('owner_user_id') for vals in vals_list if vals.get('owner_user_id')]
        if owner_ids:
            unique_owner_ids = list(set(owner_ids))
            svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
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

        group_ids = [vals.get('user_websites_group_id') for vals in vals_list if vals.get('user_websites_group_id')]
        if group_ids:
            unique_group_ids = list(set(group_ids))
            svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            global_limit = int(self.env['zero_sudo.security.utils']._get_system_param('user_websites.global_website_page_limit', 100))
            
            existing_group_counts = {g_id: 0 for g_id in unique_group_ids}
            group_counts = self.env['website.page'].with_user(svc_uid)._read_group(
                [('user_websites_group_id', 'in', unique_group_ids)],
                ['user_websites_group_id'],
                ['__count']
            )
            for group, count in group_counts:
                existing_group_counts[group.id] = count
            
            batch_group_counts = {g_id: 0 for g_id in unique_group_ids}
            for vals in vals_list:
                g_id = vals.get('user_websites_group_id')
                if g_id:
                    batch_group_counts[g_id] += 1
                    
            for g_id in unique_group_ids:
                if existing_group_counts[g_id] + batch_group_counts[g_id] > global_limit:
                    raise ValidationError(_("This group has reached its limit of %s website pages.") % global_limit)
                    
        # 3. Apply Service Account to safely bypass standard ir.ui.view creation restrictions
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
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
                user_id = self.env.user.id
                
                # ADR-0022: Pre-fetch group memberships to prevent N+1 lazy-load queries in the loop
                group_ids = self.mapped('user_websites_group_id').ids
                member_map = {}
                if group_ids:
                    svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
                    groups = self.env['user.websites.group'].with_user(svc_uid).browse(group_ids)
                    for g in groups:
                        member_map[g.id] = set(g.member_ids.ids)
                        
                for page in self:
                    is_owner = page.owner_user_id.id == user_id
                    is_group_member = page.user_websites_group_id and user_id in member_map.get(page.user_websites_group_id.id, set())
                    if not is_owner and not is_group_member:
                        from odoo.exceptions import AccessError
                        raise AccessError(_("Access Denied: You do not have permission to modify this page."))
        return super(WebsitePage, self).check_access_rule(operation)

    def write(self, vals):
        self.check_access('write')
        self._check_proxy_ownership_write(vals)
        
        if 'arch' in vals and not (self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('user_websites.group_user_websites_administrator')):
            vals['arch'] = self._sanitize_user_arch(vals['arch'])
        
        # Identify URLs to invalidate before mutating
        pages_to_invalidate = [p.url for p in self if p.url]
        
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        res = super(WebsitePage, self.with_user(svc_uid)).write(vals)
        
        # Targeted DB NOTIFY invalidation (O(1) line eviction instead of global clear)
        if 'url' in vals or 'website_published' in vals or 'is_published' in vals:
            utils = self.env['zero_sudo.security.utils']
            urls_to_notify = list(pages_to_invalidate)
            if 'url' in vals and vals['url'] not in urls_to_notify:
                urls_to_notify.append(vals['url'])
            if urls_to_notify:
                utils._notify_cache_invalidation('website.page', urls_to_notify)
                
        return res

    def unlink(self):
        self.check_access('unlink')
        
        pages_to_invalidate = [p.url for p in self if p.url]
        
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        res = super(WebsitePage, self.with_user(svc_uid)).unlink()
        
        utils = self.env['zero_sudo.security.utils']
        if pages_to_invalidate:
            utils._notify_cache_invalidation('website.page', pages_to_invalidate)
            
        return res

    @api.model
    def _flush_redis_view_counters(self):
        """
        Cron job to flush Redis view counters to the PostgreSQL database.
        Uses _trigger() for batching if there are too many keys (ADR-0022).
        """
        try:
            cursor, keys = redis_client.scan(cursor=0, match="views:page:*", count=1000)
        except Exception as e:
            _logger.error(f"Failed to connect to Redis for view counter flush: {e}")
            return

        if not keys:
            return

        pipe = redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        
        results = pipe.execute()
        
        updates = []
        for i, key in enumerate(keys):
            val = results[i]
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
                # CRITICAL: Commit to PostgreSQL before destroying the ephemeral Redis state
                from odoo import tools
                if not tools.config.get('test_enable'):
                    self.env.cr.commit()
                
                del_pipe = redis_client.pipeline()
                for key in keys:
                    del_pipe.delete(key)
                del_pipe.execute()
            except Exception as e:
                from odoo import tools
                if not tools.config.get('test_enable'):
                    self.env.cr.rollback()
                _logger.error(f"Error updating PostgreSQL view counts: {e}")
        
        if cursor != 0:
            cron = self.env.ref('user_websites.ir_cron_flush_view_counters', raise_if_not_found=False)
            if cron:
                cron._trigger()

# -*- coding: utf-8 -*-
import odoo
from odoo import models, fields, api, tools, _
from .res_users import _async_unpublish_content

class ResUsersModeration(models.Model):
    """
    Feature-specific extension of res.users to handle the 
    Three-Strikes moderation, suspension logic, and high-performance slug caching.
    """
    _inherit = 'res.users'

    violation_strike_count = fields.Integer(
        string="Violation Strikes", 
        default=0, 
        help="Number of upheld content violations. Hitting 3 triggers an automatic suspension."
    )
    is_suspended_from_websites = fields.Boolean(
        string="Suspended from Websites", 
        default=False, 
        help="If True, all personal pages and blogs are forcefully unpublished and locked."
    )

    @api.model
    @tools.ormcache('slug')
    def _get_user_id_by_slug(self, slug):
        """
        High-performance RAM cache for slug resolution.
        Prevents full DB queries on every public profile view.
        """
        if not slug:
            return False
        # Case-insensitive search requires ilike, but cache key is exact.
        # We lowercase the slug in the controller to ensure cache hits.
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user = self.env['res.users'].with_user(svc_uid).search([('website_slug', '=ilike', slug)], limit=1)
        return user.id if user else False

    def write(self, vals):
        # [%ANCHOR: slug_cache_invalidation]
        # Verified by [%ANCHOR: test_slug_cache_invalidation]
        if 'website_slug' in vals or 'active' in vals:
            slugs = [user.website_slug for user in self if user.website_slug]
            if slugs:
                self.env['zero_sudo.security.utils']._notify_cache_invalidation('res.users', slugs)

        res = super(ResUsersModeration, self).write(vals)
        
        # Emit NOTIFY for the new slug if it changed
        if 'website_slug' in vals and vals['website_slug']:
            self.env['zero_sudo.security.utils']._notify_cache_invalidation('res.users', vals['website_slug'])
            
        return res

    def unlink(self):
        # [%ANCHOR: slug_cache_invalidation_unlink]
        # Verified by [%ANCHOR: test_slug_cache_invalidation]
        slugs = [user.website_slug for user in self if user.website_slug]
        if slugs:
            self.env['zero_sudo.security.utils']._notify_cache_invalidation('res.users', slugs)

        return super(ResUsersModeration, self).unlink()

    def action_suspend_user_websites(self):
        """Forcefully unpublishes all user content and flags them as suspended."""
        user_ids = self.ids
        
        if not odoo.tools.config.get('test_enable'):
            from concurrent.futures import ThreadPoolExecutor
            db_name = self.env.cr.dbname
            # Fire and forget safely without unbounded thread growth
            ThreadPoolExecutor(max_workers=2).submit(_async_unpublish_content, db_name, user_ids)
        else:
            svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            while True:
                pages = self.env['website.page'].with_user(svc_uid).search([('owner_user_id', 'in', user_ids), '|', ('is_published', '=', True), ('website_published', '=', True)], limit=5000)
                if not pages:
                    break
                pages.write({'is_published': False, 'website_published': False})
            while True:
                posts = self.env['blog.post'].with_user(svc_uid).search([('owner_user_id', 'in', user_ids), ('is_published', '=', True)], limit=5000)
                if not posts:
                    break
                posts.write({'is_published': False})

        for user in self:
            user.is_suspended_from_websites = True
            
            # Note: We use Odoo's mail.thread on the underlying partner to log the suspension
            user.partner_id.message_post(
                body=_("🚨 **AUTOMATED ACTION:** The system suspended this user for accumulating 3 or more violation strikes and unpublished their personal content."),
                subtype_xmlid="mail.mt_note"
            )

    def action_pardon_user_websites(self):
        """Resets strikes and lifts the suspension (Does NOT automatically republish content)."""
        for user in self:
            user.violation_strike_count = 0
            user.is_suspended_from_websites = False
            user.partner_id.message_post(
                body=_("✅ **MODERATION ACTION:** You pardoned this user. The system lifted their suspension and reset their strike count to 0. (Note: Previously unpublished content remains unpublished until manually restored)."),
                subtype_xmlid="mail.mt_note"
            )

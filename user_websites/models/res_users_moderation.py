# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

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
        svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user = self.env['res.users'].with_user(svc_uid).search([('website_slug', '=ilike', slug)], limit=1)
        return user.id if user else False

    def write(self, vals):
        res = super(ResUsersModeration, self).write(vals)
        if 'website_slug' in vals:
            # Invalidate the cache via registry in Odoo 19+
            self.env.registry.clear_cache()
        return res

    def unlink(self):
        # Invalidate ORM cache before deleting the records via registry in Odoo 19+
        self.env.registry.clear_cache()
        return super(ResUsersModeration, self).unlink()

    def action_suspend_user_websites(self):
        """Forcefully unpublishes all user content and flags them as suspended."""
        svc_uid = self.env.ref('user_websites.user_user_websites_service_account').id
        for user in self:
            user.is_suspended_from_websites = True
            
            # 1. Unpublish Pages
            pages = self.env['website.page'].search([('owner_user_id', '=', user.id)])
            if pages:
                pages.with_user(svc_uid).write({'is_published': False, 'website_published': False})
                
            # 2. Unpublish Blog Posts
            blogs = self.env['blog.post'].search([('owner_user_id', '=', user.id)])
            if blogs:
                blogs.with_user(svc_uid).write({'is_published': False})

            # Note: We use Odoo's mail.thread on the underlying partner to log the suspension
            user.partner_id.message_post(
                body="🚨 **AUTOMATED ACTION:** User has been suspended from the Websites feature due to accumulating 3 or more violation strikes. All personal content has been unpublished.",
                subtype_xmlid="mail.mt_note"
            )

    def action_pardon_user_websites(self):
        """Resets strikes and lifts the suspension (Does NOT automatically republish content)."""
        for user in self:
            user.violation_strike_count = 0
            user.is_suspended_from_websites = False
            user.partner_id.message_post(
                body="✅ **MODERATION ACTION:** User has been pardoned. Suspension lifted and strike count reset to 0. (Note: Previously unpublished content remains unpublished until manually restored).",
                subtype_xmlid="mail.mt_note"
            )

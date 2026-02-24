# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'user_websites.owned.mixin']

    view_count = fields.Integer(string="View Count", default=0, help="Privacy-friendly tracking of page views.")

    @api.model_create_multi
    def create(self, vals_list):
        # 1. Enforce Mixin Security
        self._check_proxy_ownership_create(vals_list)

        # 2. Quota Limit Check
        owner_ids = [vals.get('owner_user_id') for vals in vals_list if vals.get('owner_user_id')]
        if owner_ids:
            unique_owner_ids = list(set(owner_ids))
            svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            users = self.env['res.users'].with_user(svc_uid).browse(unique_owner_ids)
            user_limits = {user.id: user._get_page_limit() for user in users}
            
            existing_pages = self.env['website.page'].with_user(svc_uid).search_read(
                [('owner_user_id', 'in', unique_owner_ids)], 
                ['owner_user_id']
            )
            
            existing_counts = {u_id: 0 for u_id in unique_owner_ids}
            for page in existing_pages:
                existing_counts[page['owner_user_id'][0]] += 1
            
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

    def write(self, vals):
        self.check_access('write')
        self._check_proxy_ownership_write(vals)
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        return super(WebsitePage, self.with_user(svc_uid)).write(vals)

    def unlink(self):
        self.check_access('unlink')
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        return super(WebsitePage, self.with_user(svc_uid)).unlink()

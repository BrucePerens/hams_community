# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, api, _
from odoo.exceptions import AccessError

class ResUsersSEO(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'website.seo.metadata']

    @api.model
    def _get_writeable_fields(self):
        """
        Allows users to securely save their own SEO metadata via the frontend 
        widget without triggering mass-assignment AccessErrors (ADR-0015).
        """
        return super()._get_writeable_fields() + [
            'website_meta_title', 
            'website_meta_description', 
            'website_meta_keywords', 
            'website_meta_og_img', 
            'seo_name'
        ]

    def check_access_rule(self, operation):
        """
        Silently suppress write access errors for SEO checks to prevent log spam.
        Odoo's frontend evaluates `check_access_rule('write')` to see if it should 
        render the "Optimize SEO" menu. Failing natively logs an INFO message.
        """
        if operation in ('write', 'unlink') and not self.env.su and self:
            if not self.env.user.has_group('base.group_system') and not self.env.user.has_group('user_websites.group_user_websites_administrator'):
                for record in self:
                    if record.id != self.env.user.id:
                        raise AccessError(_("Access Denied: You do not have permission to modify this profile."))
        return super(ResUsersSEO, self).check_access_rule(operation)

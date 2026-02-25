# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, api, _
from odoo.exceptions import AccessError

class UserWebsitesGroupSEO(models.Model):
    _name = 'user.websites.group'
    _inherit = ['user.websites.group', 'website.seo.metadata']

    def check_access_rule(self, operation):
        """
        Silently suppress write access errors for SEO checks to prevent log spam.
        """
        if operation in ('write', 'unlink') and not self.env.su and self:
            if not self.env.user.has_group('user_websites.group_user_websites_administrator'):
                for group in self:
                    if self.env.user.id not in group.member_ids.ids:
                        raise AccessError(_("Access Denied: You do not have permission to modify this group."))
        return super(UserWebsitesGroupSEO, self).check_access_rule(operation)

# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, api, _  # noqa: F401
from odoo.exceptions import AccessError

class UserWebsitesGroupSEO(models.Model):
    _name = "user.websites.group"
    _inherit = ["user.websites.group", "website.seo.metadata"]

    def check_access_rule(self, operation):
        """
        Silently suppress access errors for SEO checks to prevent log spam and allow
        the frontend widget to render and save. Odoo checks 'read' and 'write'.
        """
        if operation in ("read", "write", "unlink") and not self.env.su and self:
            if not self.env.user.has_group(
                "user_websites.group_user_websites_administrator"
            ):
                # Suppress access errors if a user is acting exclusively on groups they are a member of
                if all(self.env.user.id in group.member_ids.ids for group in self):
                    return None
        return super(UserWebsitesGroupSEO, self).check_access_rule(operation)

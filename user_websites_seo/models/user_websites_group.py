# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, _
from odoo.exceptions import AccessError

class UserWebsitesGroupSEO(models.Model):
    _name = "user.websites.group"
    _inherit = ["user.websites.group", "website.seo.metadata"]

    def write(self, vals):
        seo_fields = {"website_meta_title", "website_meta_description", "website_meta_keywords", "website_meta_og_img", "seo_name"}
        seo_vals = {k: v for k, v in vals.items() if k in seo_fields}
        other_vals = {k: v for k, v in vals.items() if k not in seo_fields}

        res = True
        if other_vals:
            # Let standard Odoo ACLs handle non-SEO writes natively
            res = super(UserWebsitesGroupSEO, self).write(other_vals)

        if seo_vals:
            if self.env.su or self.env.user.has_group("user_websites.group_user_websites_administrator"):
                res = res and super(UserWebsitesGroupSEO, self).write(seo_vals)
            else:
                if all(self.env.user.id in group.member_ids.ids for group in self):
                    # Escalate strictly for the write operation using the domain service account
                    svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid("user_websites.user_user_websites_service_account")
                    res = res and super(UserWebsitesGroupSEO, self.with_user(svc_uid)).write(seo_vals)
                else:
                    raise AccessError(_("You can only modify SEO metadata for groups you are a member of."))

        return res

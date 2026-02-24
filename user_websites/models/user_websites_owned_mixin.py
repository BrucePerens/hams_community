# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class UserWebsitesOwnedMixin(models.AbstractModel):
    """
    An abstract mixin that provides the 'Proxy Ownership' pattern to any model.
    Inherit this to securely tie a model to a user or a group website.
    """
    _name = 'user_websites.owned.mixin'
    _description = 'User Websites Proxy Ownership Mixin'

    owner_user_id = fields.Many2one(
        'res.users', 
        string="Owner", 
        index=True,
        ondelete='cascade',
        help="The user who 'owns' this record business-wise."
    )

    user_websites_group_id = fields.Many2one(
        'user.websites.group',
        string="Group Owner",
        help="The group that owns this record.",
        ondelete='cascade',
        index=True
    )

    @api.model
    def _check_proxy_ownership_create(self, vals_list):
        """Validates that the current user is legally allowed to assign the provided ownership."""
        if self.env.su or self.env.user.has_group('user_websites.group_user_websites_administrator') or self.env.user.has_group('user_websites.group_user_websites_service_account'):
            return
        for vals in vals_list:
            if vals.get('owner_user_id') and vals.get('owner_user_id') != self.env.user.id:
                raise AccessError(_("You cannot create a record owned by another user."))
            if vals.get('user_websites_group_id'):
                svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
                group = self.env['user.websites.group'].with_user(svc_uid).browse(vals['user_websites_group_id'])
                if self.env.user not in group.member_ids:
                    raise AccessError(_("You cannot create a record for a group you do not belong to."))

    def _check_proxy_ownership_write(self, vals):
        """Prevents malicious actors from spoofing or transferring ownership after creation."""
        if self.env.su or self.env.user.has_group('user_websites.group_user_websites_administrator') or self.env.user.has_group('user_websites.group_user_websites_service_account'):
            return
        if 'owner_user_id' in vals or 'user_websites_group_id' in vals:
            raise AccessError(_("You cannot transfer ownership of a record to another user or group."))

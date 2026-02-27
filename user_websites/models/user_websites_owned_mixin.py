# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError

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
        # [%ANCHOR: mixin_proxy_ownership_create]
        # Verified by [%ANCHOR: test_mixin_ownership_validation]
        # Verified by [%ANCHOR: test_api_armor_mandatory_assignment]
        """Validates that the current user is legally allowed to assign the provided ownership, enforces mandatory ownership, and prevents dual ownership."""
        for vals in vals_list:
            owner_id = vals.get('owner_user_id')
            group_id = vals.get('user_websites_group_id')
            
            if owner_id and group_id:
                raise ValidationError(_("A record cannot be owned by both a user and a group simultaneously."))
                
            if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('user_websites.group_user_websites_administrator') or self.env.user.has_group('user_websites.group_user_websites_service_account'):
                continue
                
            if not owner_id and not group_id:
                raise AccessError(_("You must assign an owner (user or group) when creating this record."))

            if owner_id and int(owner_id) != self.env.user.id:
                raise AccessError(_("You cannot create a record owned by another user."))
                
            if group_id:
                svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
                group = self.env['user.websites.group'].with_user(svc_uid).browse(int(group_id))
                if not group.exists() or self.env.user not in group.member_ids:
                    raise AccessError(_("You cannot create a record for a group you do not belong to, or the group does not exist."))

    def _check_proxy_ownership_write(self, vals):
        # [%ANCHOR: mixin_proxy_ownership_write]
        # Verified by [%ANCHOR: test_mixin_ownership_validation]
        # Verified by [%ANCHOR: test_api_armor_mutual_exclusion]
        """Prevents malicious actors from spoofing or transferring ownership after creation, and prevents admins from creating dual-owned corrupted states."""
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('user_websites.group_user_websites_administrator') or self.env.user.has_group('user_websites.group_user_websites_service_account'):
            if 'owner_user_id' in vals or 'user_websites_group_id' in vals:
                for record in self:
                    new_owner = vals.get('owner_user_id', record.owner_user_id.id if record.owner_user_id else False)
                    new_group = vals.get('user_websites_group_id', record.user_websites_group_id.id if record.user_websites_group_id else False)
                    if new_owner and new_group:
                        raise ValidationError(_("A record cannot be owned by both a user and a group simultaneously."))
            return
            
        if 'owner_user_id' in vals or 'user_websites_group_id' in vals:
            raise AccessError(_("You cannot transfer ownership of a record to another user or group."))

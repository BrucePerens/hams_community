# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_websites_administrators_ids = fields.Many2many(
        'res.users',
        relation='settings_user_websites_admin_rel',
        string="User Websites Administrators",
        help="Users with full access to manage all user websites and groups."
    )

    @api.model
    def get_values(self):
        """
        Load the current members of the Administrator group.
        """
        res = super(ResConfigSettings, self).get_values()
        admin_group = self.env.ref('user_websites.group_user_websites_administrator', raise_if_not_found=False)
        if admin_group:
            res['user_websites_administrators_ids'] = [(6, 0, admin_group.user_ids.ids)]
        else:
            res['user_websites_administrators_ids'] = [(6, 0, [])]
        return res

    def set_values(self):
        """
        Save changes by updating the Administrator group members.
        """
        super(ResConfigSettings, self).set_values()
        admin_group = self.env.ref('user_websites.group_user_websites_administrator', raise_if_not_found=False)
        if admin_group:
            svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            admin_group.with_user(svc_uid).write({
                'user_ids': [(6, 0, self.user_websites_administrators_ids.ids)]
            })

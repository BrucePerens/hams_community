# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    user_websites_administrators_ids = fields.Many2many(
        "res.users",
        relation="settings_user_websites_admin_rel",
        string="User Websites Administrators",
        help="Users with full access to manage all user websites and groups.",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        admin_group = self.env.ref(
            "user_websites.group_user_websites_administrator", raise_if_not_found=False
        )
        if admin_group:
            svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
                "user_websites.user_user_websites_service_account"
            )
            admin_users = admin_group.with_user(svc_uid).user_ids.ids
            res["user_websites_administrators_ids"] = [(6, 0, admin_users)]
        else:
            res["user_websites_administrators_ids"] = [(6, 0, [])]
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        admin_group = self.env.ref(
            "user_websites.group_user_websites_administrator", raise_if_not_found=False
        )
        if admin_group:
            svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
                "user_websites.user_user_websites_service_account"
            )
            admin_group.with_user(svc_uid).write(
                {"user_ids": [(6, 0, self.user_websites_administrators_ids.ids)]}
            )

    def action_update_python_venv(self):
        svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
            "user_websites.user_user_websites_service_account"
        )
        res = self.env["zero_sudo.security.utils"].with_user(svc_uid)._update_python_venv()
        if res:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Environment Updated"),
                    "message": _("Python dependencies have been successfully updated. Restart the Odoo service for changes to take effect."),
                    "type": "success",
                    "sticky": True,
                },
            }

# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsersZeroSudo(models.Model):
    _inherit = "res.users"

    is_service_account = fields.Boolean(
        # [@ANCHOR: is_service_account_field]
        # Verified by [@ANCHOR: test_is_service_account_field]
        # Tests [@ANCHOR: story_login_blocking]
        # Tests [@ANCHOR: journey_service_account_lifecycle]
        string="Is Service Account",
        default=False,
        help="Flags this user as an internal service account. Prevents interactive web logins.",
    )


class ResUsersApiKeysZeroSudo(models.Model):
    _inherit = "res.users.apikeys"

    @api.model
    def _check_expiration_date(self, expiration_date):
        """
        Bypass API key maximum duration constraints for Service Accounts.
        Service accounts require long-lived (90-day) rotating keys for daemon stability
        and intentionally lack the administrative groups required by core Odoo to generate them.
        """
        if self.env.user.is_service_account:
            return True
        return super()._check_expiration_date(expiration_date)

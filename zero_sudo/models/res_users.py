# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsersZeroSudo(models.Model):
    _inherit = 'res.users'

    is_service_account = fields.Boolean(
        string="Is Service Account",
        default=False,
        help="Flags this user as an internal service account. Prevents interactive web logins."
    )

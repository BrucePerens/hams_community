#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cloudflare_turnstile_secret = fields.Char(
        string='Turnstile Secret Key', 
        config_parameter='cloudflare.turnstile_secret',
        help="Used to cryptographically verify invisible CAPTCHA tokens submitted by public guests."
    )

    def action_deploy_cf_waf(self):
        from ..utils.cloudflare_api import deploy_waf_rules
        
        success, msg = deploy_waf_rules()
        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': msg,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to deploy WAF rules: %s") % msg)

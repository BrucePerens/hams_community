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
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
        success, msg = self.env['cloudflare.config.manager'].with_user(svc_uid).action_push_waf_rules()
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

    def action_pull_cf_waf(self):
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
        success, msg = self.env['cloudflare.config.manager'].with_user(svc_uid).action_pull_waf_rules()
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
            raise UserError(_("Failed to pull WAF rules: %s") % msg)

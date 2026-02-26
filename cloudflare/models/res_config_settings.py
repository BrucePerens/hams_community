#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cloudflare_api_token = fields.Char(related='website_id.cloudflare_api_token', readonly=False)
    cloudflare_zone_id = fields.Char(related='website_id.cloudflare_zone_id', readonly=False)
    cloudflare_turnstile_secret = fields.Char(related='website_id.cloudflare_turnstile_secret', readonly=False)

    def action_deploy_cf_waf(self):
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
        website_id = self.website_id.id if self.website_id else self.env['website'].get_current_website().id
        success, msg = self.env['cloudflare.config.manager'].with_user(svc_uid).action_push_waf_rules(website_id=website_id)
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
        website_id = self.website_id.id if self.website_id else self.env['website'].get_current_website().id
        success, msg = self.env['cloudflare.config.manager'].with_user(svc_uid).action_pull_waf_rules(website_id=website_id)
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

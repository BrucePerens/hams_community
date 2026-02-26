#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CloudflareIPBan(models.Model):
    _name = 'cloudflare.ip.ban'
    _description = 'Cloudflare IP Ban / Honeypot Registry'
    _order = 'create_date desc'

    ip_address = fields.Char(string="Target IP Address", required=True)
    mode = fields.Selection([
        ('block', 'Block'),
        ('challenge', 'Interactive Challenge'),
        ('managed_challenge', 'Managed Challenge (Recommended)')
    ], string="Action Applied", default='block', required=True)
    notes = fields.Char(string="Trigger Reason", default="Honeypot Triggered")
    cf_rule_id = fields.Char(string="Cloudflare Rule ID", readonly=True)
    state = fields.Selection([
        ('active', 'Active (Banned)'),
        ('lifted', 'Lifted (Unbanned)'),
        ('failed', 'API Sync Failed')
    ], string="Status", default='active')
    website_id = fields.Many2one('website', string="Website", default=lambda self: self.env['website'].get_current_website().id)

    @api.model
    def _execute_ban(self, ip_address, mode='block', notes="Honeypot Triggered", website_id=None):
        # [%ANCHOR: cf_execute_ban]
        # Verified by [%ANCHOR: test_cf_execute_ban]
        if not website_id:
            from odoo.http import request
            try:
                if request and getattr(request, 'website', False):
                    website_id = request.website.id
                else:
                    website_id = self.env['website'].get_current_website().id
            except RuntimeError:
                website_id = self.env['website'].get_current_website().id
                
        website = self.env['website'].browse(website_id)
        token, zone_id = website._get_cloudflare_credentials()
        
        from ..utils.cloudflare_api import ban_ip
        success, result = ban_ip(ip_address, mode, notes, token, zone_id)
        
        if success:
            self.env['cloudflare.ip.ban'].create({
                'ip_address': ip_address,
                'mode': mode,
                'notes': notes,
                'cf_rule_id': result,
                'state': 'active',
                'website_id': website.id
            })
            return True
        else:
            self.env['cloudflare.ip.ban'].create({
                'ip_address': ip_address,
                'mode': mode,
                'notes': f"Failed to deploy: {result}",
                'state': 'failed',
                'website_id': website.id
            })
            return False

    def action_lift_ban(self):
        # [%ANCHOR: cf_action_lift_ban]
        # Verified by [%ANCHOR: test_cf_action_lift_ban]
        from ..utils.cloudflare_api import unban_ip
        for rec in self:
            if rec.state == 'active' and rec.cf_rule_id:
                token, zone_id = rec.website_id._get_cloudflare_credentials() if rec.website_id else (None, None)
                success, msg = unban_ip(rec.cf_rule_id, token, zone_id)
                if success:
                    rec.state = 'lifted'
                else:
                    raise UserError(_("Failed to lift ban via Cloudflare API: %s") % msg)

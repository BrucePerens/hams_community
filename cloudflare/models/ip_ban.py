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
    cf_rule_id = fields.Char(string="Cloudflare Rule ID", readonly=True, help="The external ID from Cloudflare's Access Rules API.")
    state = fields.Selection([
        ('active', 'Active (Banned)'),
        ('lifted', 'Lifted (Unbanned)'),
        ('failed', 'API Sync Failed')
    ], string="Status", default='active')

    @api.model
    def _execute_ban(self, ip_address, mode='block', notes="Honeypot Triggered"):
        # [%ANCHOR: cf_execute_ban]
        # Verified by [%ANCHOR: test_cf_execute_ban]
        from ..utils.cloudflare_api import ban_ip
        success, result = ban_ip(ip_address, mode=mode, notes=notes)
        
        if success:
            self.env['cloudflare.ip.ban'].create({
                'ip_address': ip_address,
                'mode': mode,
                'notes': notes,
                'cf_rule_id': result,
                'state': 'active'
            })
            return True
        else:
            self.env['cloudflare.ip.ban'].create({
                'ip_address': ip_address,
                'mode': mode,
                'notes': f"Failed to deploy: {result}",
                'state': 'failed'
            })
            return False

    def action_lift_ban(self):
        # [%ANCHOR: cf_action_lift_ban]
        # Verified by [%ANCHOR: test_cf_action_lift_ban]
        from ..utils.cloudflare_api import unban_ip
        for rec in self:
            if rec.state == 'active' and rec.cf_rule_id:
                success, msg = unban_ip(rec.cf_rule_id)
                if success:
                    rec.state = 'lifted'
                else:
                    raise UserError(_("Failed to lift ban via Cloudflare API: %s") % msg)

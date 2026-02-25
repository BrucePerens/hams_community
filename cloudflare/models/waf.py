#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, api

class CloudflareWAF(models.AbstractModel):
    _name = 'cloudflare.waf'
    _description = 'Cloudflare WAF Interface'

    @api.model
    def ban_ip(self, ip_address, mode='block', duration=3600, notes="Honeypot Triggered"):
        """
        Instructs the Cloudflare edge to block or challenge an IP,
        and logs the incident in the local IP Ban registry.
        Note: `duration` is kept for backwards compatibility but handled by periodic cleanup if needed.
        """
        # Escalate to Service Account: Public users triggering a honeypot lack write access to the log.
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
        ban_env = self.env['cloudflare.ip.ban'].with_user(svc_uid)
        
        return ban_env._execute_ban(ip_address, mode=mode, notes=notes)

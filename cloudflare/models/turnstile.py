#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, api
from ..utils.cloudflare_api import verify_turnstile

class CloudflareTurnstile(models.AbstractModel):
    _name = 'cloudflare.turnstile'
    _description = 'Cloudflare Turnstile Interface'

    @api.model
    def verify_token(self, token, remote_ip=None):
        # [%ANCHOR: verify_turnstile_secret]
        # Verified by [%ANCHOR: test_turnstile_secret_fetch]
        """
        Verifies an invisible Turnstile challenge token submitted via an unauthenticated form.
        """
        secret = self.env['zero_sudo.security.utils']._get_system_param('cloudflare.turnstile_secret')
        
        if not secret:
            return False
            
        return verify_turnstile(token, remote_ip, secret)

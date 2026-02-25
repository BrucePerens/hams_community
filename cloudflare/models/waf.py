#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, api
from ..utils.cloudflare_api import ban_ip

class CloudflareWAF(models.AbstractModel):
    _name = 'cloudflare.waf'
    _description = 'Cloudflare WAF Interface'

    @api.model
    def ban_ip(self, ip_address, mode='block', duration=3600):
        """
        Immediately instructs the Cloudflare edge to block or challenge an IP.
        """
        return ban_ip(ip_address, mode=mode, duration=duration)

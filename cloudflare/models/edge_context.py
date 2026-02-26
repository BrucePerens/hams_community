#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.http import request

class CloudflareUtils(models.AbstractModel):
    _name = 'cloudflare.utils'
    _description = 'Cloudflare Edge Context Utilities'

    @api.model
    def get_request_context(self):
        """
        Parses Cloudflare-specific geographic and threat headers injected at the edge.
        Returns a dictionary to be used by proprietary modules for default routing.
        """
        try:
            if not request or not hasattr(request, 'httprequest'):
                return {}
            headers = request.httprequest.headers
        except RuntimeError:
            return {}
            
        return {
            'ip': headers.get('CF-Connecting-IP') or request.httprequest.remote_addr,
            'country': headers.get('CF-IPCountry'),
            'city': headers.get('CF-IPCity'),
            'longitude': headers.get('CF-IPLongitude'),
            'latitude': headers.get('CF-IPLatitude'),
            'threat_score': headers.get('CF-Threat-Score'),
        }

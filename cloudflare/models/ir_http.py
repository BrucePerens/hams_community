#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _post_dispatch(cls, response):
        """
        Intercepts the outgoing HTTP response to inject CDN caching directives.
        """
        res = super()._post_dispatch(response)
        
        if not request or not hasattr(request, 'httprequest'):
            return res
            
        path = request.httprequest.path
        
        # 1. Static Assets (Max aggressive caching: 1 year)
        if path.startswith('/web/static') or path.startswith('/theme_hams/static') or path.startswith('/ham_'):
            if '/static/' in path:
                res.headers['Cloudflare-CDN-Cache-Control'] = 'max-age=31536000'
                return res
                
        # 2. Dynamic, Authenticated, or API Routes (Zero caching)
        if any(path.startswith(prefix) for prefix in ('/my/', '/web/', '/api/')):
            res.headers['Cloudflare-CDN-Cache-Control'] = 'no-cache, no-store'
            return res
            
        # 3. Semi-Static Content (Blogs, User Websites, Classifieds)
        # Cache heavily at the edge. The purge_queue will invalidate this manually when edited.
        res.headers['Cloudflare-CDN-Cache-Control'] = 'max-age=86400'
        return res

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _post_dispatch(cls, response):
        """
        Intercepts the outgoing HTTP response to inject CDN caching directives.
        Generalized to dynamically check Odoo's public user state without requiring
        strict app dependencies.
        """
        res = super()._post_dispatch(response)
        
        if not request or not hasattr(request, 'httprequest') or not hasattr(response, 'headers'):
            return res
            
        path = request.httprequest.path
        
        # 1. Media & Assets (Max aggressive caching: 1 year)
        if any(path.startswith(prefix) for prefix in ('/web/static', '/web/assets', '/web/image', '/web/content')):
            response.headers['Cloudflare-CDN-Cache-Control'] = 'max-age=31536000'
            response.headers['Cache-Tag'] = 'odoo-static-assets'
            return res
            
        # 2. Hardcoded Dynamic or API Routes (Zero caching)
        if any(path.startswith(prefix) for prefix in ('/my/', '/web/', '/api/')):
            response.headers['Cloudflare-CDN-Cache-Control'] = 'no-cache, no-store'
            return res
            
        # 3. Dynamic State Isolation (Protecting Authenticated User Data)
        is_public = True
        if getattr(request, 'env', False) and hasattr(request.env, 'user'):
            is_public = request.env.user._is_public()
            
        if not is_public:
            response.headers['Cloudflare-CDN-Cache-Control'] = 'no-cache, no-store'
            return res
            
        # 4. Semi-Static Content (Public Website Pages, Blogs, Classifieds)
        # Cache heavily at the edge. The purge_queue will invalidate individual URLs when edited.
        response.headers['Cloudflare-CDN-Cache-Control'] = 'max-age=86400'
        return res

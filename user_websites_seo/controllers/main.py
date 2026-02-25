# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import http
from odoo.http import request
from odoo.addons.user_websites.controllers.main import UserWebsitesController

class UserWebsitesSEOController(UserWebsitesController):

    @http.route(['/<string:website_slug>/blog', '/<string:website_slug>/blog/'], type='http', auth="public", website=True)
    def user_blog_index(self, website_slug, tag=None, search=None, date_begin=None, date_end=None, page=1, **kwargs):
        # [%ANCHOR: controller_user_blog_index_seo_override]
        """
        Overrides the base blog routing to inject the SEO-aware user profile 
        into the QWeb rendering dictionary. This reactivates the interactive 
        'Optimize SEO' frontend widget for the blog owner.
        """
        # Execute the base controller logic
        response = super(UserWebsitesSEOController, self).user_blog_index(
            website_slug, 
            tag=tag, 
            search=search, 
            date_begin=date_begin, 
            date_end=date_end, 
            page=page, 
            **kwargs
        )
        
        # Intercept and modify the rendering dictionary before it hits the templating engine
        if response and hasattr(response, 'qcontext'):
            user = response.qcontext.get('profile_user')
            group = response.qcontext.get('profile_group')
            
            # Replace the empty recordset with the SEO-aware model
            if user:
                response.qcontext['main_object'] = user
            elif group:
                response.qcontext['main_object'] = group
                
        return response

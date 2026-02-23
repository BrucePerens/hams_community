# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import json
import hashlib
import hmac
from odoo import http, _
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError
from odoo.tools import consteq
from werkzeug.urls import url_encode, url_parse
import werkzeug
import logging
from ..hooks import install_knowledge_docs

_logger = logging.getLogger(__name__)

class UserWebsitesController(http.Controller):

    # --- 1. Community Directory ---
    @http.route('/community', type='http', auth="public", website=True)
    def community_directory(self, **kwargs):
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        users = request.env['res.users'].with_user(svc_uid).search([
            ('privacy_show_in_directory', '=', True),
            ('website_slug', '!=', False)
        ])
        return request.render('user_websites.community_directory', {
            'users': users,
            'default_title': "Community Directory",
            'default_description': "Discover the personal websites and blogs created by our community members."
        })

    # --- 2. Abuse Reporting ---
    @http.route('/website/report_violation', type='http', auth="public", methods=['POST'], website=True)
    def submit_violation_report(self, url='', description='', email='', website_honeypot='', **kwargs):
        url = url.strip()[:2000]
        description = description.strip()[:5000]
        
        referrer = request.httprequest.referrer or '/'
        parsed_referrer = url_parse(referrer)
        safe_redirect = parsed_referrer.path if parsed_referrer.path.startswith('/') else '/'

        # --- Anti-Spam Honeypot Enforcement ---
        honeypot = website_honeypot.strip()
        if honeypot:
            _logger.info("Spam bot detected and blocked by honeypot on violation report endpoint.")
            # Silent fail: Redirect back as if it worked to confuse automated bots
            separator = '&' if '?' in safe_redirect else '?'
            return request.redirect(f"{safe_redirect}{separator}report_submitted=1")

        if not url or not description:
            return request.redirect(safe_redirect)

        is_public = request.env.user._is_public()
        user_id = False if is_public else request.env.user.id
        
        email = email.strip()[:255]
        if not is_public and request.env.user.email:
            email = request.env.user.email
        elif not email:
            email = 'Anonymous'

        content_owner_id = False
        
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        page = request.env['website.page'].with_user(svc_uid).search([('url', '=', url)], limit=1)
        if page and page.owner_user_id:
            content_owner_id = page.owner_user_id.id
            
        if not content_owner_id:
            parts = [p for p in url.split('/') if p]
            if parts:
                potential_slug = parts[0].lower()
                cached_uid = request.env['res.users']._get_user_id_by_slug(potential_slug)
                if cached_uid:
                    content_owner_id = cached_uid

        request.env['content.violation.report'].create({
            'target_url': url,
            'description': description,
            'reported_by_user_id': user_id,
            'reported_by_email': email,
            'content_owner_id': content_owner_id,
        })
        
        separator = '&' if '?' in safe_redirect else '?'
        return request.redirect(f"{safe_redirect}{separator}report_submitted=1")

    # --- 3. Home Page Routing, Caching & View Tracking ---
    @http.route(['/<string:website_slug>', '/<string:website_slug>/home', '/<string:website_slug>/home/'], type='http', auth="public", website=True)
    def user_websites_home(self, website_slug, **kwargs):
        slug_lower = website_slug.lower()
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user_id = request.env['res.users'].with_user(svc_uid)._get_user_id_by_slug(slug_lower)
        user = request.env['res.users'].with_user(svc_uid).browse(user_id) if user_id else None

        if user:
            page = request.env['website.page'].with_user(svc_uid).search([
                ('url', '=', f'/{user.website_slug}/home'),
                ('website_published', '=', True),
                '|', ('website_id', '=', False), ('website_id', '=', request.website.id)
            ], limit=1)
            
            if page:
                page.with_user(svc_uid).write({'view_count': page.view_count + 1})
                
                # Retrieve avatar for OpenGraph og:image if available
                avatar_url = f"/web/image/res.users/{user.id}/avatar_128" if user.avatar_128 else ""

                return request.render(page.view_id.xml_id, {
                    'main_object': page,
                    'profile_user': user,
                    'is_owner': request.env.user.id == user.id,
                    'default_title': f"{user.name}'s Homepage",
                    'default_description': f"Welcome to the personal site of {user.name}.",
                    'default_image': avatar_url,
                    'resolved_slug': user.website_slug
                })
            raise werkzeug.exceptions.NotFound()

        # Fallback to Groups (Uncached fallback since we don't have the group model to edit in this phase)
        group = request.env['user.websites.group'].with_user(svc_uid).search([('website_slug', '=ilike', website_slug)], limit=1)
        if group:
            page = request.env['website.page'].with_user(svc_uid).search([
                ('url', '=', f'/{group.website_slug}/home'),
                ('website_published', '=', True),
                '|', ('website_id', '=', False), ('website_id', '=', request.website.id)
            ], limit=1)

            if page:
                page.with_user(svc_uid).write({'view_count': page.view_count + 1})
                is_member = request.env.user in group.odoo_group_id.user_ids
                return request.render(page.view_id.xml_id, {
                    'main_object': page,
                    'profile_group': group,
                    'is_owner': is_member,
                    'default_title': f"{group.name} Homepage",
                    'default_description': f"Welcome to the official page of {group.name}.",
                    'resolved_slug': group.website_slug
                })

        raise werkzeug.exceptions.NotFound()

    # --- 4. Site Creation ---
    @http.route(['/<string:website_slug>/create_site'], type='http', auth="user", methods=['POST'], website=True)
    def create_site(self, website_slug, **kwargs):
        slug_lower = website_slug.lower()
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user_id = request.env['res.users'].with_user(svc_uid)._get_user_id_by_slug(slug_lower)
        user = request.env['res.users'].with_user(svc_uid).browse(user_id) if user_id else None
        group = request.env['user.websites.group'].with_user(svc_uid).search([('website_slug', '=ilike', website_slug)], limit=1)
        
        target_uid = request.env.user.id
        resolved_slug = None

        if user:
            if user.id != request.env.user.id:
                raise AccessError(_("You do not have permission to create this site."))
            resolved_slug = user.website_slug
        elif group:
            if request.env.user not in group.odoo_group_id.user_ids:
                raise AccessError(_("You do not have permission to create this site."))
            resolved_slug = group.website_slug
        else:
            raise werkzeug.exceptions.NotFound()

        view_xml_id = 'user_websites.template_default_home'
        unique_key = f"user_websites.home_{resolved_slug}"
        
        request.env['website.page'].create({
            'url': f'/{resolved_slug}/home',
            'is_published': True,
            'website_published': True,
            'type': 'qweb',
            'website_id': request.website.id,
            'key': unique_key, 
            'view_id': request.env.ref(view_xml_id).id,
            'user_websites_group_id': group.id if group else False,
            'owner_user_id': target_uid, 
        })
        
        return request.redirect(f'/{resolved_slug}/home')

    # --- 5. Blog Routing ---
    @http.route(['/<string:website_slug>/blog', '/<string:website_slug>/blog/'], type='http', auth="public", website=True)
    def user_blog_index(self, website_slug, tag=None, search=None, date_begin=None, date_end=None, **kwargs):
        slug_lower = website_slug.lower()
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user_id = request.env['res.users'].with_user(svc_uid)._get_user_id_by_slug(slug_lower)
        user = request.env['res.users'].with_user(svc_uid).browse(user_id) if user_id else None
        group = request.env['user.websites.group'].with_user(svc_uid).search([('website_slug', '=ilike', website_slug)], limit=1)
        
        if not user and not group:
            raise werkzeug.exceptions.NotFound()

        domain = [
            ('is_published', '=', True),
            ('blog_id.name', '=', 'Community Blog'),
            '|', ('website_id', '=', False), ('website_id', '=', request.website.id)
        ]

        resolved_slug = user.website_slug if user else group.website_slug

        if user:
            domain.append(('owner_user_id', '=', user.id))
            main_object = user
            meta_title = f"{user.name}'s Blog"
        else:
            domain.append(('user_websites_group_id', '=', group.id))
            main_object = group
            meta_title = f"{group.name}'s Blog"

        posts = request.env['blog.post'].with_user(svc_uid).search(domain)
        
        blogs = request.env['blog.blog'].with_user(svc_uid).search([
            ('name', '=', 'Community Blog'),
            '|', ('website_id', '=', False), ('website_id', '=', request.website.id)
        ])

        def blog_url(tag=None, date_begin=None, date_end=None, search=None):
            url = request.httprequest.path
            params = request.httprequest.args.to_dict()
            if search is not None:
                params['search'] = search
            if tag is not None:
                params['tag'] = tag
            if date_begin is not None:
                params['date_begin'] = date_begin
            if date_end is not None:
                params['date_end'] = date_end
            
            params = {k: v for k, v in params.items() if v}
            if params:
                return f"{url}?{url_encode(params)}"
            return url

        pager = request.website.pager(
            url=f"/{resolved_slug}/blog",
            total=len(posts),
            page=1,
            step=len(posts) if posts else 10
        )

        return request.render('website_blog.blog_post_short', {
            'posts': posts,
            'blog': posts and posts[0].blog_id or (blogs[0] if blogs else False),
            'blogs': blogs, 
            'main_object': main_object, 
            'profile_user': user,     
            'profile_group': group,   
            'blog_url': blog_url,
            'tag': tag,
            'search': search,
            'pager': pager,
            'default_title': meta_title,
            'default_description': f"Read the latest updates and posts on {meta_title}.",
            'resolved_slug': resolved_slug
        })

    # --- 6. Blog Creation ---
    @http.route(['/<string:website_slug>/create_blog'], type='http', auth="user", methods=['POST'], website=True)
    def create_blog_post(self, website_slug, **kwargs):
        slug_lower = website_slug.lower()
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user_id = request.env['res.users'].with_user(svc_uid)._get_user_id_by_slug(slug_lower)
        user = request.env['res.users'].with_user(svc_uid).browse(user_id) if user_id else None
        group = request.env['user.websites.group'].with_user(svc_uid).search([('website_slug', '=ilike', website_slug)], limit=1)
        
        resolved_slug = None

        if user:
            if user.id != request.env.user.id:
                raise AccessError(_("You cannot create posts for this user."))
            resolved_slug = user.website_slug
        elif group:
            if request.env.user not in group.odoo_group_id.user_ids:
                raise AccessError(_("You do not have permission to create posts for this group."))
            resolved_slug = group.website_slug
        else:
            raise werkzeug.exceptions.NotFound()

        blog = request.env['blog.blog'].with_user(svc_uid).search([
            ('name', '=', 'Community Blog'),
            '|', ('website_id', '=', False), ('website_id', '=', request.website.id)
        ], limit=1)
        
        if not blog:
            blog = request.env['blog.blog'].with_user(svc_uid).create({
                'name': 'Community Blog',
                'website_id': request.website.id
            })

        request.env['blog.post'].create({
            'name': "Welcome to my Blog" if user else f"Welcome to the {group.name} Blog",
            'blog_id': blog.id,
            'is_published': True,
            'website_id': request.website.id,
            'content': "<p>This is my first post!</p>",
            'owner_user_id': request.env.user.id,
            'user_websites_group_id': group.id if group else False
        })

        return request.redirect(f'/{resolved_slug}/blog')

    # --- 7. Documentation ---
    @http.route('/user-websites/documentation', type='http', auth="user", website=True)
    def user_websites_documentation(self, **kwargs):
        if 'knowledge.article' in request.env:
            article = install_knowledge_docs(request.env)
            if article and hasattr(article, 'website_url') and article.website_url:
                return request.redirect(article.website_url)
                
        return request.render('user_websites.documentation_page', {})

    # --- 8. Moderation Appeals ---
    @http.route('/website/submit_appeal', type='http', auth="user", methods=['POST'], website=True)
    def submit_appeal(self, reason='', **kwargs):
        reason = reason.strip()[:5000]
        user = request.env.user
        
        if user.is_suspended_from_websites and reason:
            svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            existing = request.env['content.violation.appeal'].with_user(svc_uid).search([
                ('user_id', '=', user.id), 
                ('state', '=', 'new')
            ])
            if not existing:
                request.env['content.violation.appeal'].create({
                    'user_id': user.id,
                    'reason': reason
                })
                
        return request.redirect('/my/home?appeal_submitted=1')

    # --- 9. Subscriptions & Unsubscribes ---
    @http.route('/<string:website_slug>/subscribe', type='http', auth="user", methods=['POST'], website=True)
    def subscribe_to_site(self, website_slug, **kwargs):
        slug_lower = website_slug.lower()
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        user_id = request.env['res.users'].with_user(svc_uid)._get_user_id_by_slug(slug_lower)
        user = request.env['res.users'].with_user(svc_uid).browse(user_id) if user_id else None
        group = request.env['user.websites.group'].with_user(svc_uid).search([('website_slug', '=ilike', website_slug)], limit=1)
        
        target_record = user.partner_id if user else group
        if target_record:
            target_record.with_user(svc_uid).message_subscribe(partner_ids=[request.env.user.partner_id.id])
            
        referrer = request.httprequest.referrer or '/'
        return request.redirect(f"{referrer}?subscribed=1")

    @http.route('/website/unsubscribe/<string:model_name>/<int:record_id>/<int:partner_id>/<string:token>', type='http', auth="public", website=True)
    def unsubscribe_digest(self, model_name, record_id, partner_id, token, **kwargs):
        if model_name not in ['res.partner', 'user.websites.group']:
            raise werkzeug.exceptions.NotFound()
            
        svc_uid = request.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        record = request.env[model_name].with_user(svc_uid).browse(record_id)
        if not record.exists():
            raise werkzeug.exceptions.NotFound()
            
        db_secret = request.env['ir.config_parameter'].sudo().get_param('database.secret', 'default_secret')  # burn-ignore
        message = f"{model_name}-{record_id}-{partner_id}".encode('utf-8')
        expected_token = hmac.new(db_secret.encode('utf-8'), message, hashlib.sha256).hexdigest()
        
        if not consteq(token, expected_token):
            raise werkzeug.exceptions.Forbidden()
            
        record.with_user(svc_uid).message_unsubscribe(partner_ids=[partner_id])
        
        return request.render('user_websites.unsubscribe_success', {
            'record_name': record.name
        })

    # --- 10. GDPR Privacy & Data Subject Access ---
    @http.route(['/my/privacy'], type='http', auth="user", website=True)
    def my_privacy_dashboard(self, **kwargs):
        """Renders the frontend portal dashboard for data portability and right to erasure."""
        return request.render('user_websites.portal_my_privacy', {
            'default_title': "My Privacy Dashboard"
        })

    @http.route(['/my/privacy/export'], type='http', auth="user", website=True)
    def export_user_data(self, **kwargs):
        """Compiles user generated content into a machine-readable JSON format for data portability."""
        user = request.env.user
        data = user._get_gdpr_export_data()
        
        json_data = json.dumps(data, indent=4)
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Disposition', content_disposition(f"{user.website_slug}_data_export.json"))
        ]
        return request.make_response(json_data, headers=headers)

    @http.route(['/my/privacy/delete_content'], type='http', auth="user", methods=['POST'], website=True)
    def delete_user_content(self, **kwargs):
        """Fulfills the 'Right to Erasure' by permanently unlinking all owned content."""
        request.env.user._execute_gdpr_erasure()
        return request.redirect('/my/privacy?erased=1')

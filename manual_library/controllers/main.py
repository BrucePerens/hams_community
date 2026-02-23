# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug.exceptions

class ManualLibraryController(http.Controller):

    @http.route(['/manual', '/manual/<string:article_slug>'], type='http', auth="public", website=True)
    def manual_article_view(self, article_slug=None, **kwargs):
        """
        Public/Frontend controller to render articles. 
        Enforces access securely through the ORM environment.
        """
        article = None
        
        # 1. Manually extract the ID and fetch the record to allow ORM rules to handle visibility
        if article_slug:
            try:
                article_id = int(article_slug.split('-')[0])
                article = request.env['knowledge.article'].browse(article_id)
                if not article.exists():
                    raise werkzeug.exceptions.NotFound()
            except (ValueError, IndexError):
                raise werkzeug.exceptions.NotFound()

        # 2. Fetch root articles for the sidebar navigation and group dynamically
        root_articles = request.env['knowledge.article'].search([('parent_id', '=', False)])
        
        workspace_articles = root_articles.filtered(lambda a: a.internal_permission in ('read', 'write'))
        private_articles = root_articles.filtered(lambda a: a.internal_permission == 'none' and a.create_uid == request.env.user and not a.member_ids)
        shared_articles = root_articles.filtered(lambda a: a.internal_permission == 'none' and request.env.user in a.member_ids)

        # 3. If no specific article is requested, default to the first available root article
        if not article and root_articles:
            if workspace_articles:
                article = workspace_articles[0]
            elif shared_articles:
                article = shared_articles[0]
            elif private_articles:
                article = private_articles[0]

        # 4. Handle 404s gracefully
        if not article or not article.exists():
            raise werkzeug.exceptions.NotFound()

        # 5. Enforce Read Context (Public/Guest)
        try:
            article.check_access('read')
            _ = article.name 
        except Exception:
            raise werkzeug.exceptions.NotFound()

        # 6. Render standard QWeb response
        return request.render('manual_library.article_template', {
            'main_object': article,
            'article': article,
            'workspace_articles': workspace_articles,
            'shared_articles': shared_articles,
            'private_articles': private_articles,
            'search_term': '',
        })

    @http.route(['/manual/search'], type='http', auth="public", website=True)
    def manual_search(self, search='', **kwargs):
        """
        Provides full-text search across accessible articles.
        """
        domain = []
        if search:
            domain += ['|', ('name', 'ilike', search), ('body', 'ilike', search)]
        
        # Removed .sudo() to allow native Record Rules to filter visibility by user persona
        articles = request.env['knowledge.article'].search(domain)
        
        # Fetch and group root articles for the sidebar navigation
        root_articles = request.env['knowledge.article'].search([('parent_id', '=', False)])
        workspace_articles = root_articles.filtered(lambda a: a.internal_permission in ('read', 'write'))
        private_articles = root_articles.filtered(lambda a: a.internal_permission == 'none' and a.create_uid == request.env.user and not a.member_ids)
        shared_articles = root_articles.filtered(lambda a: a.internal_permission == 'none' and request.env.user in a.member_ids)
        
        return request.render('manual_library.search_results_template', {
            'articles': articles,
            'search_term': search,
            'workspace_articles': workspace_articles,
            'shared_articles': shared_articles,
            'private_articles': private_articles,
        })

    @http.route(['/manual/feedback'], type='http', auth="public", methods=['POST'], website=True)
    def manual_feedback(self, article_id, is_helpful, website_feedback_honeypot=None, **kwargs):
        """
        Handles article helpfulness ratings via Service Account isolation.
        """
        # --- ANTI-SPAM: Honeypot Check ---
        if website_feedback_honeypot:
            referer = request.httprequest.referrer or '/manual'
            return request.redirect(referer)
            
        try:
            # Fetch without sudo() first to ensure the user actually has Read access to the article
            article = request.env['knowledge.article'].browse(int(article_id))
            if article.exists():
                # Escalate to Service Account ONLY for the write operation since guests lack write permissions
                svc_uid = request.env.ref('manual_library.user_manual_library_service_account').id
                if is_helpful == '1':
                    article.with_user(svc_uid).write({'helpful_count': article.helpful_count + 1})
                else:
                    article.with_user(svc_uid).write({'unhelpful_count': article.unhelpful_count + 1})
        except Exception:
            # Silently fail on bad input to prevent brute-force discovery
            pass
            
        # Protect against open redirects by enforcing local paths
        referer = request.httprequest.referrer or '/manual'
        parsed_referrer = werkzeug.urls.url_parse(referer)
        safe_redirect = parsed_referrer.path if parsed_referrer.path.startswith('/') else '/manual'
        
        separator = '&' if '?' in safe_redirect else '?'
        return request.redirect(f"{safe_redirect}{separator}feedback_submitted=1")

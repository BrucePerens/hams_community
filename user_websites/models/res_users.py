# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
"""
This file extends the built-in Odoo `res.users` model to add fields and logic
specific to the user websites functionality.
"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
from ..utils import slugify

RESERVED_SLUGS = {
    'community', 'blog', 'website', 'contactus', 'aboutus', 'forum', 'shop', 'my', 'web'
}

class ResUsers(models.Model):
    """
    Inherits from `res.users` to add features for personal user websites.
    """
    _inherit = 'res.users'

    # --- Field Definitions ---
    website_slug = fields.Char(
        string="Website Slug",
        help="The URL-friendly identifier for the user's site. Alphanumeric and hyphens only."
    )

    website_page_limit = fields.Integer(
        string="Website Page Limit",
        help="Maximum number of pages this user can create. If 0, the global limit is used."
    )

    privacy_show_in_directory = fields.Boolean(
        string="Show in Public Directory",
        help="If checked, a link to this user's website will appear in the public community directory.",
        default=False
    )

    # --- Inverse Relationships (Bidirectional Integrity) ---
    user_websites_page_ids = fields.One2many(
        'website.page',
        'owner_user_id',
        string="Owned Website Pages",
        help="Pages owned by this user."
    )

    user_websites_blog_post_ids = fields.One2many(
        'blog.post',
        'owner_user_id',
        string="Owned Blog Posts",
        help="Blog posts authored by this user."
    )

    submitted_violation_report_ids = fields.One2many(
        'content.violation.report',
        'reported_by_user_id',
        string="Submitted Violation Reports",
        help="Reports submitted by this user."
    )

    received_violation_report_ids = fields.One2many(
        'content.violation.report',
        'content_owner_id',
        string="Received Violation Reports",
        help="Reports filed against content owned by this user."
    )
    
    appeal_ids = fields.One2many(
        'content.violation.appeal',
        'user_id',
        string="Moderation Appeals"
    )

    # --- Odoo 19 Constraint Syntax ---
    _website_slug_unique = models.Constraint(
        'UNIQUE(website_slug)',
        'The Website Slug must be unique!'
    )

    _website_slug_format = models.Constraint(
        r"CHECK(website_slug IS NULL OR website_slug = '' OR website_slug ~ '^[a-z0-9\-]+$')",
        'The Website Slug can only contain lowercase letters, numbers, and hyphens.'
    )

    @api.constrains('website_slug')
    def _check_reserved_slugs(self):
        for record in self:
            if record.website_slug and record.website_slug in RESERVED_SLUGS:
                raise ValidationError(_("The slug '%s' is reserved and cannot be used.") % record.website_slug)

    # --- Slug Generation & Management ---

    @api.model
    def _generate_unique_slug(self, base_string, record_id=False):
        """
        Generates a URL-safe, globally unique slug. Cross-references reserved routes,
        other users, and groups.
        """
        if not base_string:
            return ''
        
        base_slug = slugify(base_string)
        slug = base_slug
        counter = 1
        max_retries = 1000
        
        while True:
            if counter > max_retries:
                raise ValidationError(_("Unable to generate a unique website slug after %s attempts.") % max_retries)
            
            if slug in RESERVED_SLUGS:
                slug = f"{base_slug}-{counter}"
                counter += 1
                continue
            
            user_domain = [('website_slug', '=', slug)]
            if record_id:
                user_domain.append(('id', '!=', record_id))
            
            svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            user_collision = self.env['res.users'].with_user(svc_uid).search_count(user_domain)
            group_collision = self.env['user.websites.group'].with_user(svc_uid).search_count([('website_slug', '=', slug)])
            
            if not user_collision and not group_collision:
                return slug
                
            slug = f"{base_slug}-{counter}"
            counter += 1

    @api.model_create_multi
    def create(self, vals_list):
        """
        Intercept creation to inject a default generated slug if none was explicitly provided.
        """
        for vals in vals_list:
            if vals.get('website_slug'):
                vals['website_slug'] = self._generate_unique_slug(vals['website_slug'])
            elif vals.get('name'):
                vals['website_slug'] = self._generate_unique_slug(vals['name'])
                
        return super(ResUsers, self).create(vals_list)

    def write(self, vals):
        old_slugs = {}
        if 'website_slug' in vals:
            # Safely format the incoming slug directly
            if vals.get('website_slug'):
                if len(self) == 1:
                    vals['website_slug'] = self._generate_unique_slug(vals['website_slug'], record_id=self.id)
                else:
                    # If bulk updating, enforce formatting but let DB handle collision detection
                    vals['website_slug'] = slugify(vals['website_slug'])
                    
            old_slugs = {user.id: user.website_slug for user in self if user.website_slug}

        # --- Content Lifecycle Policy ---
        if 'active' in vals and not vals['active']:
            users_to_archive = self.ids
            svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            self.env['website.page'].with_user(svc_uid).search([
                ('owner_user_id', 'in', users_to_archive)
            ]).write({'website_published': False})
            
            self.env['blog.post'].with_user(svc_uid).search([
                ('owner_user_id', 'in', users_to_archive)
            ]).write({'is_published': False})

        try:
            result = super(ResUsers, self).write(vals)
        except IntegrityError:
            self.env.cr.rollback()
            raise ValidationError(_("The Website Slug must be unique and valid."))

        # --- 301 Redirect Automation ---
        if 'website_slug' in vals:
            svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
            redirect_env = self.env['website.redirect'].with_user(svc_uid)
            for user in self:
                old_slug = old_slugs.get(user.id)
                new_slug = user.website_slug
                if old_slug and new_slug and old_slug != new_slug:
                    redirects = [{
                        'url_from': f'/{old_slug}',
                        'url_to': f'/{new_slug}',
                        'type': '301',
                        'website_id': False,
                    }]
                    if self.env['blog.post'].with_user(svc_uid).search_count([('owner_user_id', '=', user.id)]) > 0:
                        redirects.append({
                            'url_from': f'/{old_slug}/blog',
                            'url_to': f'/{new_slug}/blog',
                            'type': '301',
                            'website_id': False,
                        })
                    redirect_env.create(redirects)

        return result

    # --- Business & GDPR Extensible Methods ---

    def _get_page_limit(self):
        self.ensure_one()
        limit = self.website_page_limit
        if not limit or limit <= 0:
            limit = self.env['ham.security.utils']._get_system_param(
                'user_websites.global_website_page_limit', 100
            )
        return int(limit)

    def _get_gdpr_export_data(self):
        """
        Returns a dictionary of all personal data and authored content for GDPR portability.
        """
        self.ensure_one()
        svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        pages = self.env['website.page'].with_user(svc_uid).search([('owner_user_id', '=', self.id)])
        blogs = self.env['blog.post'].with_user(svc_uid).search([('owner_user_id', '=', self.id)])
        reports = self.env['content.violation.report'].with_user(svc_uid).search([('reported_by_user_id', '=', self.id)])
        appeals = self.env['content.violation.appeal'].with_user(svc_uid).search([('user_id', '=', self.id)])
        
        return {
            'user': {
                'name': self.name, 
                'email': self.email, 
                'website_slug': self.website_slug
            },
            'pages': [
                {'name': p.name, 'url': p.url, 'content': p.arch} for p in pages
            ],
            'blog_posts': [
                {'name': b.name, 'content': b.content, 'published_date': str(b.post_date)} for b in blogs
            ],
            'submitted_reports': [
                {'target_url': r.target_url, 'description': r.description, 'status': r.state, 'submitted_date': str(r.create_date)} for r in reports
            ],
            'appeals': [
                {'reason': a.reason, 'status': a.state, 'submitted_date': str(a.create_date)} for a in appeals
            ]
        }

    def _execute_gdpr_erasure(self):
        """
        Executes the GDPR right to erasure by hard-deleting all authored content.
        """
        self.ensure_one()
        svc_uid = self.env['ham.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        
        # [%ANCHOR: gdpr_sudo_erasure]
        # ADR-0017: sudo() is required here to ensure cascaded data not owned by the service account is successfully purged.
        self.env['website.page'].sudo().search([('owner_user_id', '=', self.id)]).unlink()  # burn-ignore
        self.env['blog.post'].sudo().search([('owner_user_id', '=', self.id)]).unlink()  # burn-ignore
        
        self.with_user(svc_uid).write({'privacy_show_in_directory': False})

        if hasattr(super(), '_execute_gdpr_erasure'):
            super()._execute_gdpr_erasure()

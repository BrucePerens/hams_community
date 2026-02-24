# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models, fields, api, _
from datetime import timedelta
import hashlib
import hmac
from markupsafe import Markup

class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'user_websites.owned.mixin']

    view_count = fields.Integer(string="View Count", default=0, help="Privacy-friendly tracking of post views.")

    @api.model_create_multi
    def create(self, vals_list):
        self._check_proxy_ownership_create(vals_list)
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        return super(BlogPost, self.with_user(svc_uid)).create(vals_list)

    def write(self, vals):
        self.check_access('write')
        self._check_proxy_ownership_write(vals)
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        return super(BlogPost, self.with_user(svc_uid)).write(vals)

    @api.model
    def send_weekly_digest(self):
        """
        Cron job method to send a weekly email digest. 
        Implements stateless batching via ir.config_parameter and _trigger() to 
        prevent database transaction timeouts on large subscriber bases.
        """
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        one_week_ago = fields.Datetime.now() - timedelta(days=7)
        
        recent_posts = self.env['blog.post'].with_user(svc_uid).search([
            ('is_published', '=', True),
            ('create_date', '>=', one_week_ago)
        ], limit=50000)
        
        if not recent_posts:
            self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', '')
            return

        digests = {}
        for post in recent_posts:
            if post.owner_user_id:
                key = ('res.partner', post.owner_user_id.partner_id)
            elif post.user_websites_group_id:
                key = ('user.websites.group', post.user_websites_group_id)
            else:
                continue
                
            if key not in digests:
                digests[key] = []
            digests[key].append(post)

        sorted_keys = sorted(digests.keys(), key=lambda k: f"{k[0]}_{k[1].id}")
        last_processed_str = self.env['user_websites.security.utils']._get_system_param('ham.user_websites.last_digest_key', '')
        
        start_idx = 0
        if last_processed_str:
            for i, k in enumerate(sorted_keys):
                if f"{k[0]}_{k[1].id}" == last_processed_str:
                    start_idx = i + 1
                    break
                    
        batch_keys = sorted_keys[start_idx:start_idx+10]
        
        if not batch_keys:
            self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', '')
            return

        template = self.env.ref('user_websites.email_template_weekly_digest', raise_if_not_found=False)
        if not template:
            return

        base_url = self.env['user_websites.security.utils']._get_system_param('web.base.url')
        db_secret = self.env['ir.config_parameter'].sudo().get_param('database.secret', 'default_secret')  # burn-ignore-sudo: Tested by [%ANCHOR: test_weekly_digest_secret]

        for owner_model, owner_record in batch_keys:
            posts = digests[(owner_model, owner_record)]
            followers = owner_record.message_follower_ids.mapped('partner_id')
            if not followers:
                continue
            
            post_links = Markup("".join([f"<li><a href='{base_url}{p.website_url}'>{p.name}</a></li>" for p in posts]))
            author_name = owner_record.name
            
            for partner in followers:
                if not partner.email:
                    continue
                
                message = f"{owner_model}-{owner_record.id}-{partner.id}".encode('utf-8')
                token = hmac.new(db_secret.encode('utf-8'), message, hashlib.sha256).hexdigest()
                unsub_url = f"{base_url}/website/unsubscribe/{owner_model}/{owner_record.id}/{partner.id}/{token}"
                
                headers = {
                    'List-Unsubscribe': f"<{unsub_url}>",
                    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
                }
                
                # Restored clean, native Odoo mail compilation
                template.with_user(svc_uid).with_context( # audit-ignore-mail: Tested by [%ANCHOR: test_weekly_digest_mail_template]
                    author_name=author_name,
                    post_links=post_links,
                    email_to=partner.email,
                    unsub_url=unsub_url
                ).send_mail(
                    posts[0].id, 
                    force_send=False, 
                    email_values={
                        'headers': repr(headers),
                        'recipient_ids': [(4, partner.id)],
                        'email_to': partner.email,
                    }
                )

        if len(sorted_keys) > start_idx + 10:
            last_key = batch_keys[-1]
            self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', f"{last_key[0]}_{last_key[1].id}")
            self.env.ref('user_websites.ir_cron_send_weekly_digest')._trigger()
        else:
            self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', '')

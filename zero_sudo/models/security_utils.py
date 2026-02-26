#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, api, tools, _
from odoo.exceptions import AccessError

PARAM_WHITELIST = frozenset([
    'web.base.url',
    'ham_dns.base_domain',
    'cloudflare.last_static_mtime',
    'ham_dns.default_a_record_ip',
    'ham.user_websites.last_digest_key',
    'user_websites.global_website_page_limit',
    'user_websites.company_abuse_email',
    'cloudflare.turnstile_secret',
])

class ZeroSudoSecurityUtils(models.AbstractModel):
    _name = 'zero_sudo.security.utils'
    _description = 'Centralized Security and Privilege Utilities'

    @api.model
    @tools.ormcache('xml_id')
    def _get_service_uid(self, xml_id):
        # [%ANCHOR: get_service_uid]
        # Verified by [%ANCHOR: test_get_service_uid]
        uid = self.env['ir.model.data'].sudo()._xmlid_to_res_id(xml_id)
        if not uid:
            raise AccessError(_("Security Alert: Service Account '%s' not found.") % xml_id)
        self.env.cr.execute("SELECT active FROM res_users WHERE id = %s", (uid,))
        res = self.env.cr.fetchone()
        if not res or not res[0]:
            raise AccessError(_("Security Alert: Service Account is disabled."))
        return uid

    @api.model
    def _notify_cache_invalidation(self, model_name, key_value):
        # [%ANCHOR: coherent_cache_signal]
        # Verified by [%ANCHOR: test_coherent_cache_signal]
        self.env.cr.execute("SELECT pg_notify(%s, %s)", ('ham_cache_invalidation', f"{model_name}:{key_value}"))

    @api.model
    def _get_system_param(self, key, default=None):
        if key not in PARAM_WHITELIST:
            raise AccessError(_("Security Alert: Parameter '%s' is not whitelisted for extraction.") % key)
        return self.env['ir.config_parameter'].sudo().get_param(key, default)

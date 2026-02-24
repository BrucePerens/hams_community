#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.
from odoo import models, api, tools, _
from odoo.exceptions import AccessError

# Strict whitelist to prevent arbitrary parameter extraction via RPC or QWeb SSTI.
# NEVER whitelist 'database.secret' or other cryptographic keys here.
PARAM_WHITELIST = frozenset([
    'web.base.url',
    'ham_dns.base_domain',
    'ham_dns.default_a_record_ip',
    'ham.user_websites.last_digest_key',
    'user_websites.global_website_page_limit',
    'user_websites.company_abuse_email',
])

class UserWebsitesSecurityUtils(models.AbstractModel):
    _name = 'user_websites.security.utils'
    _description = 'Centralized Security and Privilege Utilities'

    @api.model
    @tools.ormcache('xml_id')
    def _get_service_uid(self, xml_id):
        """
        Safely retrieves a Service Account ID without requiring inline sudo().
        Prefix '_' prevents XML-RPC Skeleton Key exposure.
        """
        # [%ANCHOR: get_service_uid]
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
        """
        Emits a PostgreSQL NOTIFY to maintain phase coherence across distributed workers.
        """
        # [%ANCHOR: coherent_cache_signal]
        self.env.cr.execute("SELECT pg_notify(%s, %s)", ('ham_cache_invalidation', f"{model_name}:{key_value}"))

    @api.model
    def _get_system_param(self, key, default=None):
        """
        Safely retrieves a whitelisted system parameter without requiring inline sudo().
        Prefix '_' prevents XML-RPC Skeleton Key exposure.
        """
        if key not in PARAM_WHITELIST:
            raise AccessError(_("Security Alert: Parameter '%s' is not whitelisted for extraction.") % key)
        return self.env['ir.config_parameter'].sudo().get_param(key, default)

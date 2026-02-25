#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class CloudflareWafRule(models.Model):
    _name = 'cloudflare.waf.rule'
    _description = 'Cloudflare WAF Custom Rule'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequence", default=10, help="Execution order in Cloudflare.")
    name = fields.Char(string="Rule Name", required=True)
    action = fields.Selection([
        ('block', 'Block'),
        ('challenge', 'Interactive Challenge'),
        ('managed_challenge', 'Managed Challenge (Recommended)'),
        ('js_challenge', 'JS Challenge'),
        ('skip', 'Skip / Allow')
    ], string="Action", required=True, default='managed_challenge')
    expression = fields.Text(string="Expression", required=True, help="Cloudflare Wirefilter Expression (e.g., http.request.uri.path contains \"/xmlrpc\")")
    description = fields.Text(string="Comments / Documentation", help="Profuse comments sent to Cloudflare to explain this rule to sysadmins.")
    active = fields.Boolean(string="Active", default=True)

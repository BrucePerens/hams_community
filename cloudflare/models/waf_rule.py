#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class CloudflareWafRule(models.Model):
    _name = 'cloudflare.waf.rule'
    _description = 'Cloudflare WAF Custom Rule'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string="Rule Name", required=True)
    action = fields.Selection([
        ('block', 'Block'),
        ('challenge', 'Interactive Challenge'),
        ('managed_challenge', 'Managed Challenge (Recommended)'),
        ('js_challenge', 'JS Challenge'),
        ('skip', 'Skip / Allow')
    ], string="Action", required=True, default='managed_challenge')
    expression = fields.Text(string="Expression", required=True)
    description = fields.Text(string="Comments / Documentation")
    active = fields.Boolean(string="Active", default=True)
    website_id = fields.Many2one('website', string="Website", required=True, default=lambda self: self.env['website'].get_current_website().id)

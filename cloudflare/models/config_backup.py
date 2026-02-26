#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class CloudflareConfigBackup(models.Model):
    _name = 'cloudflare.config.backup'
    _description = 'Cloudflare Configuration Backup'
    _order = 'create_date desc'

    name = fields.Char(string="Backup Name", required=True)
    phase = fields.Char(string="Ruleset Phase", default="http_request_firewall_custom")
    raw_json = fields.Text(string="Raw JSON Payload", required=True)
    create_date = fields.Datetime(string="Backed Up On", readonly=True)
    website_id = fields.Many2one('website', string="Website", default=lambda self: self.env['website'].get_current_website().id)

# -*- coding: utf-8 -*-
from odoo import models, fields


class CloudflareConfigBackup(models.Model):
    _name = "cloudflare.config.backup"
    _description = "Cloudflare Configuration Backup"
    _order = "create_date desc"

    name = fields.Char(string="Backup Name", required=True)
    phase = fields.Char(string="Ruleset Phase", default="http_request_firewall_custom")
    raw_json = fields.Text(string="Raw JSON Payload", required=True)
    create_date = fields.Datetime(string="Backed Up On", readonly=True)
    website_id = fields.Many2one(
        "website",
        string="Website",
        default=lambda self: self.env["website"].get_current_website().id,
    )


    _sql_constraints = [
        (
            "name_not_empty",
            "CHECK(LENGTH(TRIM(name)) > 0)",
            "The backup name cannot be empty.",
        ),
        (
            "json_not_empty",
            "CHECK(LENGTH(TRIM(raw_json)) > 0)",
            "The JSON payload cannot be empty.",
        ),
    ]
    _sql_constraints = [
        ('_name_website_uniq', 'UNIQUE(name, website_id)', 'A backup with this name already exists for this website!'),
    ]

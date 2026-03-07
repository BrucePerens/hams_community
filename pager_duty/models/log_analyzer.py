#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class PagerLogPattern(models.Model):
    _name = "pager.log.pattern"
    _description = "Log Analyzer Regex Pattern"
    _order = "severity desc, name asc"

    name = fields.Char(string="Pattern Name", required=True, help="e.g. Kernel Filesystem Corruption")
    regex = fields.Char(string="Regular Expression", required=True, help="e.g. (ext4|xfs|btrfs).*error")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Severity",
        default="high",
        required=True
    )
    active = fields.Boolean(default=True)

class PagerLogFile(models.Model):
    _name = "pager.log.file"
    _description = "Log Analyzer Target File"

    filepath = fields.Char(string="Absolute Path", required=True, help="e.g. /var/log/syslog")
    active = fields.Boolean(default=True)

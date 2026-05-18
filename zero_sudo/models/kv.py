# -*- coding: utf-8 -*-
from odoo import models, fields

class ZeroSudoKV(models.Model):
    _name = "zero_sudo.kv"
    _description = "Zero-Sudo Key-Value Store"

    key = fields.Char(string="Key", required=True)
    value = fields.Text(string="Value")

    _key_uniq = models.Constraint("UNIQUE(key)", "The key must be mathematically unique.")

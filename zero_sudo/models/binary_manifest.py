#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class ZeroSudoBinaryManifest(models.Model):
    _name = "zero_sudo.binary.manifest"
    _description = "Binary Download Manifest"

    name = fields.Char(string="Binary Name", required=True, help="Command name (e.g., kopia)")
    url = fields.Char(string="Download URL", required=True)
    checksum = fields.Char(string="SHA-256 Checksum", required=True)
    archive_type = fields.Selection([
        ('binary', 'Raw Binary'),
        ('tar.gz', 'Tarball (.tar.gz)')
    ], string="Archive Type", default="binary", required=True)
    extract_member = fields.Char(string="Extract Member", help="Specific file to extract from the archive.")

    _name_uniq = models.Constraint("UNIQUE(name)", "The binary name must be unique!")

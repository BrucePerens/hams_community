#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields

class CloudflareTunnelWizard(models.TransientModel):
    _name = 'cloudflare.tunnel.wizard'
    _description = 'Cloudflare Tunnel Setup Wizard'

    command = fields.Text(string="Installation Command", readonly=True)

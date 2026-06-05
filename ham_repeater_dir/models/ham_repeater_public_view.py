# -*- coding: utf-8 -*-
from odoo import models, fields

class HamRepeaterPublicView(models.Model):
    _name = "ham.repeater.public.view"
    _description = "Public Repeater Directory View"
    _auto = False

    callsign = fields.Char(readonly=True)
    name = fields.Char(readonly=True)
    output_frequency = fields.Float(readonly=True)
    city = fields.Char(readonly=True)
    state_id = fields.Many2one("res.country.state", readonly=True)
    allow_web_transceiver = fields.Boolean(readonly=True)

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS ham_repeater_public_view CASCADE;")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW ham_repeater_public_view AS
            SELECT
                id,
                callsign,
                name,
                output_frequency,
                city,
                state_id,
                allow_web_transceiver
            FROM ham_repeater
        """)

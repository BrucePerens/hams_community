# -*- coding: utf-8 -*-
from odoo import models

class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def _register_hook(self):
        super()._register_hook()

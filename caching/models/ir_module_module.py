# -*- coding: utf-8 -*-
from odoo import models
from ..hooks import install_knowledge_docs

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _register_hook(self):
        super()._register_hook()
        try:
            install_knowledge_docs(self.env)
        except Exception:
            pass

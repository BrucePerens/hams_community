# -*- coding: utf-8 -*-
from odoo import models, api
from ..hooks import install_knowledge_docs

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _register_hook(self):
        super()._register_hook()
        # This runs at the end of the registry loading process
        # We only want to trigger it once when the module itself or something that could enable the docs is ready.
        # However, ADR-0055 and the requirement suggest waiting until all modules are installed.
        # _register_hook on any model will run after registry is ready.
        # We use a system parameter to ensure we only try this once per registry load or once ever?
        # Requirement: "Wait until all modules are installed"
        # In Odoo, _register_hook is called after the registry is fully loaded.

        # We use the sudo context to check/set the parameter
        utils = self.env['zero_sudo.security.utils']
        try:
            # We check if we already installed it in this registry lifecycle or if it's already there
            # Actually, install_knowledge_docs already checks if it exists.
            # To avoid doing it on every single request if it fails, maybe a flag?
            # But it's better to just call it.
            install_knowledge_docs(self.env)
        except Exception:
            # Silent failure during boot to avoid blocking Odoo
            pass

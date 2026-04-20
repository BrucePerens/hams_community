# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo import models

class ComplianceConfig(models.AbstractModel):
    _name = "compliance.config"
    _description = "Compliance Configuration Hook"

    def _register_hook(self):
        """
        Ensures documentation is installed if the required models are available.
        This runs after all modules are loaded.
        """
        super()._register_hook()
        from ..hooks import install_knowledge_docs  # noqa: E402
        install_knowledge_docs(self.env)

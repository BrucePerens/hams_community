# -*- coding: utf-8 -*-
from odoo import models, fields
from ..hooks import install_knowledge_docs

class NoisyTable(models.Model):
    _name = 'test_real_transaction.noisy_table'
    _description = 'Noisy Table'

    name = fields.Char(string='Table Name', required=True, help='Name of the PostgreSQL table to ignore in leak detection.')
    active = fields.Boolean(default=True, help='If unchecked, it will allow leak detection for this table.')

    _name_uniq = models.Constraint('UNIQUE(name)', 'The table name must be unique!')

    def _register_hook(self):
        """
        Wait until all modules are installed and the registry is fully loaded
        before attempting to install documentation.
        """
        # [@ANCHOR: documentation_bootstrap]
        super()._register_hook()
        if self.env.registry.ready:
            install_knowledge_docs(self.env)

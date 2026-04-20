# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestDocumentation(TransactionCase):

    def test_documentation_installed(self):
        """Verify that the caching documentation is correctly installed in knowledge.article."""
        if "knowledge.article" not in self.env:
            self.skipTest("knowledge.article model not available")

        article = self.env["knowledge.article"].search([("name", "=", "Caching Module Documentation")], limit=1)
        self.assertTrue(article, "Caching Module Documentation should be created.")
        self.assertIn("Caching Module", article.body)
        self.assertEqual(article.icon, "⚡")

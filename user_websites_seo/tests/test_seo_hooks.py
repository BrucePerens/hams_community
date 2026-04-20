# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.addons.user_websites_seo.hooks import post_init_hook

class TestSEOHooks(TransactionCase):

    def test_post_init_hook_documentation(self):
        """Test that the documentation is correctly installed by the hook."""
        # Ensure knowledge.article exists (it should, as we depend on manual_library)
        if "knowledge.article" not in self.env:
            self.skipTest("knowledge.article model not found")

        # Run the hook
        post_init_hook(self.env)

        # Check if the article was created
        article = self.env['knowledge.article'].search([('name', '=', 'User Websites SEO Guide')], limit=1)
        self.assertTrue(article, "Documentation article should have been created")
        self.assertIn("User Websites SEO Guide", article.body, "Documentation body should contain the expected title")
        self.assertEqual(article.icon, "🔍")

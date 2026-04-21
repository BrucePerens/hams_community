# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.addons.user_websites_seo.hooks import post_init_hook

class TestSEOHooks(TransactionCase):

    def test_post_init_hook_documentation(self):
        # [@ANCHOR: test_soft_dependency_docs_installation]
        # Tests [@ANCHOR: soft_dependency_docs_installation]
        # Verified by [@ANCHOR: test_soft_dependency_docs_installation]
        """Test that the documentation is correctly installed by the hook."""
        article_model_name = None
        if "knowledge.article" in self.env:
            article_model_name = "knowledge.article"
        elif "manual.article" in self.env:
            article_model_name = "manual.article"

        if not article_model_name:
            self.skipTest("No compatible documentation model found")

        # Run the hook
        post_init_hook(self.env)

        # Check if the article was created
        article = self.env[article_model_name].search([('name', '=', 'User Websites SEO Guide')], limit=1)
        self.assertTrue(article, "Documentation article should have been created")
        self.assertIn("User Websites SEO Guide", article.body, "Documentation body should contain the expected title")
        self.assertEqual(article.icon, "🔍")

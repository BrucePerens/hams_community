# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo.tests.common import TransactionCase, tagged
from lxml import etree
import re


@tagged("post_install", "-at_install")
class TestCompliancePages(TransactionCase):

    def test_pages_presence(self):
        """Verify that legal pages are created."""
        urls = [
            "/privacy",
            "/cookie-policy",
            "/terms"
        ]
        pages = self.env["website.page"].search([("url", "in", urls)])
        found_urls = pages.mapped("url")
        for url in urls:
            self.assertIn(url, found_urls, f"Page for {url} should exist.")

        for page in pages:
            self.assertTrue(page.is_published, f"Page for {page.url} should be published.")

    def test_pages_content(self):
        """Verify that legal pages contain the expected boilerplate content."""
        for xml_id in ["compliance.compliance_privacy_policy_template",
                       "compliance.compliance_cookie_policy_template",
                       "compliance.compliance_terms_of_service_template"]:
            view = self.env.ref(xml_id)
            # Use get_combined_arch to verify the view is well-formed
            arch_node = view._get_combined_arch()
            self.assertIsNotNone(arch_node)

            # Serialize the node to string for content checking
            arch_str = etree.tostring(arch_node, encoding='unicode')

            # Normalize whitespace for checking
            normalized_arch = re.sub(r'\s+', ' ', arch_str)

            self.assertIn("Last Updated:", normalized_arch)
            self.assertIn("Warning: This is the default version", normalized_arch)
            self.assertIn("It was not produced by a lawyer.", normalized_arch)

    def test_knowledge_article_installation(self):
        """Verify the documentation article is correctly installed in knowledge.article."""
        if "knowledge.article" not in self.env:
            self.skipTest("knowledge.article model not available")

        article = self.env["knowledge.article"].search([
            ("name", "=", "Site Owner's Guide to Regulatory Compliance")
        ], limit=1)
        self.assertTrue(article, "Documentation article should have been created.")
        self.assertIn("GDPR", article.body)
        self.assertIn("WCAG", article.body)
        self.assertEqual(article.icon, "⚖️")

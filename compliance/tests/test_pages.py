# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
from odoo.tests.common import TransactionCase, HttpCase, tagged
from lxml import etree
import re


@tagged("post_install", "-at_install")
class TestCompliancePages(TransactionCase):

    def test_pages_presence(self):
        """Verify that legal pages are created."""
        # [@ANCHOR: test_compliance_pages_presence]
        # Tests [@ANCHOR: compliance_privacy_policy_template]
        # Tests [@ANCHOR: compliance_cookie_policy_template]
        # Tests [@ANCHOR: compliance_terms_of_service_template]
        # Tests [@ANCHOR: story_automatic_legal_pages]
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

@tagged("post_install", "-at_install")
class TestCompliancePagesHttp(HttpCase):

    def test_pages_reachable(self):
        """Verify that legal pages are reachable via HTTP."""
        # Tests [@ANCHOR: compliance_privacy_policy_template]
        # Tests [@ANCHOR: compliance_cookie_policy_template]
        # Tests [@ANCHOR: compliance_terms_of_service_template]
        # Tests [@ANCHOR: story_automatic_legal_pages]
        urls = [
            "/privacy",
            "/cookie-policy",
            "/terms"
        ]
        for url in urls:
            response = self.url_open(url)
            self.assertEqual(response.status_code, 200, f"Page {url} should be reachable.")
            # Use regex to ignore potential tags/whitespace around the text
            self.assertTrue(re.search(r"Last Updated:", response.text), f"Page {url} should contain boilerplate content.")

    def test_pages_content(self):
        """Verify that legal pages contain the expected boilerplate content."""
        # [@ANCHOR: test_compliance_pages_content]
        # Tests [@ANCHOR: compliance_privacy_policy_template]
        # Tests [@ANCHOR: compliance_cookie_policy_template]
        # Tests [@ANCHOR: compliance_terms_of_service_template]
        # Tests [@ANCHOR: story_automatic_legal_pages]
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
        """Verify the documentation article is correctly installed."""
        # [@ANCHOR: test_compliance_knowledge_article_installation]
        # Tests [@ANCHOR: compliance_install_knowledge_docs]
        # Tests [@ANCHOR: story_compliance_documentation]
        article_model_name = None
        if "knowledge.article" in self.env:
            article_model_name = "knowledge.article"
        elif "manual.article" in self.env:
            article_model_name = "manual.article"

        if not article_model_name:
            self.skipTest("Neither knowledge.article nor manual.article model available")

        article = self.env[article_model_name].search([
            ("name", "=", "Site Owner's Guide to Regulatory Compliance")
        ], limit=1)
        self.assertTrue(article, "Documentation article should have been created.")
        self.assertIn("GDPR", article.body)
        self.assertIn("WCAG", article.body)
        self.assertEqual(article.icon, "⚖️")

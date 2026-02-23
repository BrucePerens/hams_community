# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import unittest
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.compliance.hooks import post_init_hook

@tagged('post_install', '-at_install')
class TestComplianceHooks(TransactionCase):

    def test_01_post_init_hook_documentation(self):
        """
        Verify that the post_init_hook successfully reads the HTML file
        and installs the documentation into the knowledge.article API.
        """
        if 'knowledge.article' not in self.env:
            raise unittest.SkipTest("knowledge.article API is not installed. Skipping documentation hook test.")

        # Manually trigger the hook to ensure execution during the test transaction
        post_init_hook(self.env)
        
        article = self.env['knowledge.article'].sudo().search([
            ('name', '=', 'Site Owner\'s Guide to Regulatory Compliance')
        ], limit=1)
        
        self.assertTrue(
            article, 
            "The compliance documentation article must be created by the hook."
        )
        
        # Verify file_open successfully read the HTML content, not the error fallback
        self.assertIn(
            'Data Privacy', 
            article.body, 
            "The article body should contain the content from the HTML file."
        )
        self.assertNotIn(
            'Error loading documentation file', 
            article.body, 
            "The file_open utility should not have failed."
        )

    def test_02_post_init_hook_cookie_bar(self):
        """
        Verify that the post_init_hook successfully enables the cookies_bar
        on all websites.
        """
        if 'cookies_bar' not in self.env['website']._fields:
            raise unittest.SkipTest("'cookies_bar' field is not present on the website model. Skipping cookie bar hook test.")

        post_init_hook(self.env)
        
        websites = self.env['website'].sudo().search([])
        for website in websites:
            self.assertTrue(
                website.cookies_bar, 
                f"Cookie bar must be enabled on website: {website.name}"
            )


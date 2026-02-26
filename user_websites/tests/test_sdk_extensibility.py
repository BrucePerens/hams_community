# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import odoo.tests
from odoo.exceptions import AccessError

@odoo.tests.common.tagged('post_install', '-at_install')
class TestSDKExtensibility(odoo.tests.common.TransactionCase):
    """
    Tests the extensibility hooks provided for dependent modules, 
    including the GDPR methods, Proxy Ownership Mixin, and QWeb navbar.
    """
    
    def setUp(self):
        super(TestSDKExtensibility, self).setUp()
        self.user = self.env['res.users'].create({
            'name': 'SDK Tester',
            'login': 'sdktester',
            'email': 'sdk@example.com',
            'website_slug': 'sdktester',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })

    def test_01_gdpr_export_hook(self):
        # [%ANCHOR: test_gdpr_export_hook]
        # Tests [%ANCHOR: res_users_gdpr_export]
        """Test that the _get_gdpr_export_data method returns the correct extensible dictionary."""
        # Create a page for the user
        self.env['website.page'].create({
            'url': f'/{self.user.website_slug}/sdk-page',
            'name': 'SDK Page',
            'type': 'qweb',
            'owner_user_id': self.user.id
        })
        
        data = self.user._get_gdpr_export_data()
        streams = self.user._get_gdpr_streamed_keys()
        
        self.assertIn('user', data, "Export data must contain 'user' key.")
        self.assertIn('pages', streams, "Export stream MUST isolate 'pages' key to prevent OOM.")
        self.assertIn('blog_posts', streams, "Export stream MUST isolate 'blog_posts' key.")
        self.assertEqual(data['user']['name'], 'SDK Tester')
        
        page_generator = streams['pages']()
        generated_pages = list(page_generator)
        
        self.assertEqual(len(generated_pages), 1, "The created page must be yielded by the generator.")
        self.assertEqual(generated_pages[0]['name'], 'SDK Page')

    def test_02_gdpr_erasure_hook(self):
        """Test that the _execute_gdpr_erasure method successfully unlinks content."""
        page = self.env['website.page'].create({
            'url': f'/{self.user.website_slug}/delete-me',
            'name': 'Delete Me',
            'type': 'qweb',
            'owner_user_id': self.user.id
        })
        self.assertTrue(page.exists())
        
        self.user.write({'privacy_show_in_directory': True})
        
        # Execute the model-level hook
        self.user._execute_gdpr_erasure()
        
        self.assertFalse(page.exists(), "The hook must cascade and delete owned records.")
        self.assertFalse(self.user.privacy_show_in_directory, "The user must be removed from the directory.")

    def test_03_mixin_ownership_validation(self):
        # [%ANCHOR: test_mixin_ownership_validation]
        # Tests [%ANCHOR: mixin_proxy_ownership_create]
        # Tests [%ANCHOR: mixin_proxy_ownership_write]
        """Verify the user_websites.owned.mixin methods directly catch spoofing."""
        intruder = self.env['res.users'].create({
            'name': 'Intruder',
            'login': 'intruder2',
            'website_slug': 'intruder2',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })
        
        # Intruder attempts to create a page but assigns ownership to SDK Tester
        with self.assertRaises(AccessError, msg="Mixin must block cross-user creation attempts."):
            self.env['website.page'].with_user(intruder).create({
                'url': '/bad-page',
                'name': 'Bad Page',
                'type': 'qweb',
                'owner_user_id': self.user.id
            })

    def test_04_navbar_rendering(self):
        """Test the standalone user_navbar template renders with a mock context."""
        # Render the template directly via the QWeb engine
        rendered = self.env['ir.qweb']._render('user_websites.user_navbar', {
            'resolved_slug': self.user.website_slug,
            'profile_user': self.user,
            'profile_group': False,
        })
        
        rendered_str = str(rendered)
        self.assertIn(f'{self.user.website_slug}/home', rendered_str, "Navbar must inject the resolved_slug into links.")
        self.assertIn('SDK Tester', rendered_str, "Navbar must display the profile_user name.")

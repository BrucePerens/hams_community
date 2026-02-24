# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError

@tagged('post_install', '-at_install')
class TestPageLimits(TransactionCase):
    
    def setUp(self):
        super(TestPageLimits, self).setUp()
        
        # User with a strict personal limit of 2 pages
        self.user_limited = self.env['res.users'].create({
            'name': 'Limited User',
            'login': 'limiteduser',
            'email': 'limited@example.com',
            'website_slug': 'limiteduser',
            'website_page_limit': 2,
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id, 
                self.env.ref('user_websites.group_user_websites_user').id
            ])],
        })

        # User with 0 limit, relying on the global system parameter
        self.user_global = self.env['res.users'].create({
            'name': 'Global Limit User',
            'login': 'globaluser',
            'email': 'global@example.com',
            'website_slug': 'globaluser',
            'website_page_limit': 0,
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id, 
                self.env.ref('user_websites.group_user_websites_user').id
            ])],
        })
        
        # Set the global fallback limit to 3 for testing purposes
        self.env['ir.config_parameter'].set_param('user_websites.global_website_page_limit', '3')

    def test_01_user_specific_limit_enforcement(self):
        """
        Verify that a user with a specific limit can create pages up to that limit, 
        and is blocked upon exceeding it.
        """
        # Create pages up to the limit (2 pages)
        for i in range(2):
            self.env['website.page'].create({
                'url': f'/limiteduser/page-{i}',
                'name': f'Page {i}',
                'type': 'qweb',
                'owner_user_id': self.user_limited.id
            })
        
        # Attempt to create one more page past the limit
        with self.assertRaises(ValidationError, msg="User should not be able to exceed their personal page limit."):
            self.env['website.page'].create({
                'url': '/limiteduser/page-excess',
                'name': 'Excess Page',
                'type': 'qweb',
                'owner_user_id': self.user_limited.id
            })

    def test_02_global_limit_fallback_enforcement(self):
        """
        Verify that if a user's specific limit is 0, the system correctly falls back
        to the global ir.config_parameter limit.
        """
        # Create pages up to the global limit (3 pages)
        for i in range(3):
            self.env['website.page'].create({
                'url': f'/globaluser/page-{i}',
                'name': f'Global Page {i}',
                'type': 'qweb',
                'owner_user_id': self.user_global.id
            })
        
        # Attempt to create one more page past the global limit
        with self.assertRaises(ValidationError, msg="User should be blocked by the global limit fallback."):
            self.env['website.page'].create({
                'url': '/globaluser/page-excess',
                'name': 'Excess Global Page',
                'type': 'qweb',
                'owner_user_id': self.user_global.id
            })

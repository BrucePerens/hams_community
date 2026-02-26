# -*- coding: utf-8 -*-
from odoo.tests.common import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestModeration(HttpCase):

    def setUp(self):
        super(TestModeration, self).setUp()
        
        # 1. Create a misbehaving user
        self.bad_user = self.env['res.users'].create({
            'name': 'Spammer',
            'login': 'spammer',
            'email': 'spam@example.com',
            'website_slug': 'spammer',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })
        
        # 2. Give them some published content
        self.spam_page = self.env['website.page'].create({
            'url': f'/{self.bad_user.website_slug}/home',
            'name': 'Spam Home',
            'type': 'qweb',
            'arch': '<t name="Spam Home" t-name="user_websites.spam_home"><div>Spam</div></t>',
            'owner_user_id': self.bad_user.id,
            'is_published': True,
            'website_published': True
        })
        
        blog = self.env['blog.blog'].create({'name': 'Community Blog'})
        
        self.spam_post = self.env['blog.post'].create({
            'name': 'Spam Post',
            'blog_id': blog.id,
            'owner_user_id': self.bad_user.id,
            'is_published': True
        })

    def test_01_three_strikes_suspension(self):
        # [%ANCHOR: test_moderation_suspension]
        # Tests [%ANCHOR: action_take_action_and_strike]
        """
        Verify that hitting 3 strikes automatically suspends the user 
        and unpublishes all their content.
        """
        # Ensure starting state is clean
        self.assertEqual(self.bad_user.violation_strike_count, 0)
        self.assertFalse(self.bad_user.is_suspended_from_websites)
        self.assertTrue(self.spam_page.is_published)
        self.assertTrue(self.spam_post.is_published)

        # Admin creates and processes 3 reports
        for i in range(3):
            report = self.env['content.violation.report'].create({
                'target_url': f'/test/spam/{i}',
                'description': f'Spam instance {i}',
                'content_owner_id': self.bad_user.id
            })
            report.action_take_action_and_strike()

        # Verify final state
        self.assertEqual(self.bad_user.violation_strike_count, 3)
        self.assertTrue(self.bad_user.is_suspended_from_websites, "User should be suspended after 3 strikes.")
        
        # Verify Content was unpublished
        self.assertFalse(self.spam_page.is_published, "Page should be forcefully unpublished.")
        self.assertFalse(self.spam_post.is_published, "Blog post should be forcefully unpublished.")

    def test_02_pardon_functionality(self):
        """Verify the pardon action resets strikes and lifts suspension."""
        self.bad_user.violation_strike_count = 3
        self.bad_user.action_suspend_user_websites()
        
        self.assertTrue(self.bad_user.is_suspended_from_websites)
        
        # Admin pardons user
        self.bad_user.action_pardon_user_websites()
       
        self.assertEqual(self.bad_user.violation_strike_count, 0)
        self.assertFalse(self.bad_user.is_suspended_from_websites)
        # Note: We intentionally do NOT automatically republish content during a pardon. 
        # The user must do that manually to ensure they reviewed it.
        self.assertFalse(self.spam_page.is_published)

    def test_03_suspension_public_access_leak(self):
        """
        Verify that action_suspend_user_websites strictly revokes public access 
        and does not inadvertently set or leave public access grants during unpublication.
        """
        # Ensure page is public
        self.authenticate(None, None)
        res = self.url_open(f'/{self.bad_user.website_slug}/home')
        self.assertEqual(res.status_code, 200)
        
        # Suspend user
        self.bad_user.violation_strike_count = 3
        self.bad_user.action_suspend_user_websites()
        
        # Attempt public access again
        res_after = self.url_open(f'/{self.bad_user.website_slug}/home')
        self.assertEqual(res_after.status_code, 404, "Suspended pages must return 404 for public guests to prevent access leaks.")

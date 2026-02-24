# -*- coding: utf-8 -*-
import odoo.tests
from odoo.exceptions import AccessError

@odoo.tests.common.tagged('post_install', '-at_install')
class TestAuditEdgeCases(odoo.tests.common.TransactionCase):
    """
    Advanced integration tests targeting edge cases discovered during 
    the architectural audit of the user_websites module.
    """

    def setUp(self):
        super(TestAuditEdgeCases, self).setUp()
        
        self.test_user = self.env['res.users'].create({
            'name': 'Edge Case User',
            'login': 'edgeuser',
            'email': 'edge@example.com',
            'website_slug': 'edgeuser',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })

    def test_01_gdpr_erasure_suspended_user(self):
        """
        Verify that a suspended user (whose content is unpublished and locked) 
        can still legally exercise their Right to Erasure.
        """
        # 1. Create User Content
        page = self.env['website.page'].create({
            'url': f'/{self.test_user.website_slug}/home',
            'name': 'Home',
            'type': 'qweb',
            'owner_user_id': self.test_user.id
        })
        
        # 2. Force a Suspension (3 Strikes)
        self.test_user.violation_strike_count = 3
        self.test_user.action_suspend_user_websites()
        self.assertTrue(self.test_user.is_suspended_from_websites)
        self.assertFalse(page.website_published, "Page should be unpublished by suspension.")
        
        # 3. Execute GDPR Erasure
        self.test_user._execute_gdpr_erasure()
        
        # 4. Verify permanent deletion
        self.assertFalse(page.exists(), "Suspended user content must be fully unlinked on GDPR erasure, not just unpublished.")

    def test_02_cron_batching_resumption(self):
        # [%ANCHOR: test_cron_batching_resumption]
        """
        Verify that the weekly digest cron successfully parses the last_digest_key 
        and resumes processing from the correct index.
        """
        # Ensure a clean state for the system parameter
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', '')
        
        blog = self.env['blog.blog'].search([('name', '=', 'Community Blog')], limit=1)
        if not blog:
            blog = self.env['blog.blog'].create({'name': 'Community Blog'})
            
        self.env['blog.post'].create({
            'name': 'Cron Test Post',
            'blog_id': blog.id,
            'owner_user_id': self.test_user.id,
            'is_published': True
        })
        
        # Simulate an interrupted batch by explicitly setting the last_digest_key to this user's partner
        # The key format is "{model}_{id}"
        simulated_key = f"res.partner_{self.test_user.partner_id.id}"
        self.env['ir.config_parameter'].with_user(svc_uid).set_param('ham.user_websites.last_digest_key', simulated_key)
        
        # Run the cron method directly
        self.env['blog.post'].send_weekly_digest()
        
        # Because the key was set to our test user, the batching logic should skip them.
        # If there are no users after them in the DB state, the cron should cleanly finish and clear the key.
        final_key = self.env['user_websites.security.utils']._get_system_param('ham.user_websites.last_digest_key')
        self.assertFalse(final_key, "Cron must safely clear the digest key after completing the remaining queue.")

    def test_03_service_account_tamper_resistance(self):
        """
        Verify that if the Zero-Sudo Service Account is tampered with (e.g., archived), 
        the proxy ownership mixin fails closed securely.
        """
        svc_uid = self.env['user_websites.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        svc_user = self.env['res.users'].browse(svc_uid)
        
        # Simulate an administrator accidentally archiving the crucial service account
        svc_user.active = False
        
        # The creation of a website.page utilizes the service account internally via with_user(svc_uid)
        # to bypass the strict Odoo base UI constraints. It must fail safely if the user is inactive.
        with self.assertRaises(Exception, msg="System must fail closed if the service account is disabled, denying record creation."):
            self.env['website.page'].with_user(self.test_user).create({
                'url': f'/{self.test_user.website_slug}/fail-test',
                'name': 'Fail Page',
                'type': 'qweb',
                'owner_user_id': self.test_user.id
            })

    def test_04_bdd_ormcache_query_counting_slugs(self):
        """
        BDD: Given ADR-0049 Cache Verification
        When resolving slugs repeatedly
        Then it MUST execute exactly 0 SQL queries from cache, and invalidation MUST trigger SQL.
        """
        user = self.env['res.users'].create({
            'name': 'Cache User',
            'login': 'cache_user',
            'website_slug': 'cacheuser'
        })
        
        # 1. Prime the cache
        self.env['res.users']._get_user_id_by_slug('cacheuser')
        
        # 2. Verify 0 queries on hit
        with self.assertQueryCount(0):
            self.env['res.users']._get_user_id_by_slug('cacheuser')
            
        # 3. Trigger Invalidation
        user.write({'website_slug': 'newslug'})
        
        # 4. Verify cache was cleared (next call must execute SQL)
        with self.assertRaises(AssertionError, msg="Cache invalidation failed: Expected SQL queries to be executed."):
            with self.assertQueryCount(0):
                self.env['res.users']._get_user_id_by_slug('newslug')

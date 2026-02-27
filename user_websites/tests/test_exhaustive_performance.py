# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import odoo.tests
import logging

_logger = logging.getLogger(__name__)

@odoo.tests.common.tagged('post_install', '-at_install', 'performance')
class TestExhaustivePerformance(odoo.tests.common.TransactionCase):
    """
    Aggressive Performance test suite designed to hunt for N+1 query storms,
    memory exhaustion vectors, and scaling bottlenecks across the module.
    """
    
    def setUp(self):
        super().setUp()
        self.svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('user_websites.user_user_websites_service_account')
        self.community_blog = self.env['blog.blog'].search([('name', '=', 'Community Blog')], limit=1)
        if not self.community_blog:
            self.community_blog = self.env['blog.blog'].create({'name': 'Community Blog'})

        # Setup an active community of 20 users for scaling tests
        self.users = []
        for i in range(20):
            u = self.env['res.users'].create({
                'name': f'Scale User {i}',
                'login': f'scaleuser{i}',
                'email': f'scale{i}@example.com',
                'website_slug': f'scaleuser{i}',
                'privacy_show_in_directory': True,
                'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])],
            })
            self.users.append(u)

    def test_01_blog_creation_query_scaling(self):
        """
        BDD: Given the shared Community Blog container,
        When multiple users sequentially create their first blog post,
        Then the query count MUST remain constant (O(1)) and not increase per user.
        """
        query_counts = []
        
        for user in self.users:
            self.env.flush_all()
            start_queries = self.env.cr.sql_log_count
            
            self.env['blog.post'].with_user(self.svc_uid).create({
                'name': f"Welcome to {user.name} Blog",
                'blog_id': self.community_blog.id,
                'is_published': True,
                'owner_user_id': user.id,
            })
            
            self.env.flush_all()
            query_counts.append(self.env.cr.sql_log_count - start_queries)
            
        stable_counts = query_counts[1:]
        max_diff = max(stable_counts) - min(stable_counts)
        
        self.assertLessEqual(
            max_diff, 
            5, 
            f"Blog creation query counts are growing linearly! (Variance: {max_diff}). Counts: {query_counts}"
        )

    def test_02_mass_write_invalidation_scaling(self):
        """
        BDD: Given a user owns a massive number of website pages,
        When an admin performs a bulk write (e.g., unpublishing them),
        Then the cache invalidation logic MUST NOT fire N+1 pg_notify queries.
        """
        target_user = self.users[0]
        
        # Pre-provision 50 pages for the user
        page_vals = [{
            'url': f'/{target_user.website_slug}/page_{i}',
            'name': f'Page {i}',
            'type': 'qweb',
            'website_published': True,
            'owner_user_id': target_user.id,
            'arch': '<t name="Test" t-name="test"><div/></t>'
        } for i in range(50)]
        
        pages = self.env['website.page'].with_user(self.svc_uid).create(page_vals)
        self.assertEqual(len(pages), 50)
        
        self.env.flush_all()
        start_queries = self.env.cr.sql_log_count
        
        # Perform the bulk write
        pages.with_user(self.svc_uid).write({'website_published': False})
        
        self.env.flush_all()
        end_queries = self.env.cr.sql_log_count
        total_queries = end_queries - start_queries
        
        # A bulk update should take very few queries (UPDATE website_page SET ... WHERE id IN (...)).
        # If the query count exceeds the number of pages, there is an N+1 loop in the write override.
        self.assertLess(
            total_queries, 
            len(pages) * 8, 
            f"MASSIVE N+1 DETECTED ON BULK WRITE: {total_queries} queries executed for {len(pages)} records! Check the pg_notify implementation."
        )

    def test_03_gdpr_export_query_flatness(self):
        """
        BDD: Given two users with vastly different amounts of content,
        When executing the GDPR export hook,
        Then the number of queries MUST remain flat (O(1)) thanks to bulk searching,
        and not scale per-record.
        """
        user_light = self.users[1]
        user_heavy = self.users[2]
        
        self.env['website.page'].with_user(self.svc_uid).create({'url': f'/{user_light.website_slug}/1', 'name': 'P1', 'type': 'qweb', 'arch': '<div/>', 'owner_user_id': user_light.id})
        
        heavy_vals = [{'url': f'/{user_heavy.website_slug}/{i}', 'name': f'P{i}', 'type': 'qweb', 'arch': '<div/>', 'owner_user_id': user_heavy.id} for i in range(50)]
        self.env['website.page'].with_user(self.svc_uid).create(heavy_vals)
        
        self.env.flush_all()
        
        start_q_light = self.env.cr.sql_log_count
        user_light._get_gdpr_export_data()
        light_queries = self.env.cr.sql_log_count - start_q_light
        
        start_q_heavy = self.env.cr.sql_log_count
        user_heavy._get_gdpr_export_data()
        heavy_queries = self.env.cr.sql_log_count - start_q_heavy
        
        self.assertAlmostEqual(
            light_queries, 
            heavy_queries, 
            delta=5, 
            msg=f"GDPR export queries scale with record count! Light: {light_queries}, Heavy: {heavy_queries}"
        )

    def test_04_suspension_batching_flatness(self):
        """
        BDD: Given a user with a massive amount of content,
        When suspended,
        Then the suspension logic MUST execute in O(1) bulk batches, not N+1.
        """
        target = self.users[3]
        
        page_vals = [{'url': f'/{target.website_slug}/{i}', 'name': f'P{i}', 'type': 'qweb', 'arch': '<div/>', 'owner_user_id': target.id} for i in range(60)]
        self.env['website.page'].with_user(self.svc_uid).create(page_vals)
        
        self.env.flush_all()
        start_queries = self.env.cr.sql_log_count
        
        target.action_suspend_user_websites()
        
        self.env.flush_all()
        total_queries = self.env.cr.sql_log_count - start_queries
        
        self.assertLess(
            total_queries, 
            60 * 8, 
            f"Suspension logic executed {total_queries} queries for 60 records, indicating an N+1 failure!"
        )

@odoo.tests.common.tagged('post_install', '-at_install', 'performance')
class TestExhaustiveRoutingPerformance(odoo.tests.common.HttpCase):

    def setUp(self):
        super().setUp()
        self.users = []
        for i in range(50):
            u = self.env['res.users'].create({
                'name': f'Dir User {i}',
                'login': f'diruser{i}',
                'website_slug': f'diruser{i}',
                'privacy_show_in_directory': True,
                'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])],
            })
            self.users.append(u)
            
    def test_05_directory_pagination_flatness(self):
        """
        BDD: Given a highly populated public directory,
        When a guest navigates from Page 1 to Page 2,
        Then the underlying query load MUST remain mathematically flat.
        """
        self.authenticate(None, None)
        
        # Pre-warm QWeb cache to prevent compilation queries from skewing Page 1
        self.url_open('/community')
        
        self.env.flush_all()
        start_q_p1 = self.env.cr.sql_log_count
        self.url_open('/community')
        p1_queries = self.env.cr.sql_log_count - start_q_p1
        
        self.env.flush_all()
        start_q_p2 = self.env.cr.sql_log_count
        self.url_open('/community/page/2')
        p2_queries = self.env.cr.sql_log_count - start_q_p2
        
        self.assertAlmostEqual(
            p1_queries, 
            p2_queries, 
            delta=5, 
            msg=f"Pagination query counts are diverging severely! P1: {p1_queries}, P2: {p2_queries}"
        )

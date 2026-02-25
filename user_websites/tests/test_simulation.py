# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import odoo.tests
import secrets
import os
import logging

_logger = logging.getLogger(__name__)

@odoo.tests.common.tagged('post_install', '-at_install', '-standard', 'simulation')
class TestLongRunningSimulation(odoo.tests.common.HttpCase):
    """
    Executes a high-speed simulation to exercise system capabilities 
    over a specified number of iterations.
    """
    
    def setUp(self):
        super(TestLongRunningSimulation, self).setUp()
        self.admin = self.env.ref('base.user_admin')
        
        # Ensure the admin has the explicit User Websites Administrator group for testing access rules
        self.admin.write({'group_ids': [(4, self.env.ref('user_websites.group_user_websites_administrator').id)]})
        
        # Setup an active community of 20 users
        self.users = []
        for i in range(20):
            u = self.env['res.users'].create({
                'name': f'Sim User {i}',
                'login': f'simuser{i}',
                'email': f'sim{i}@example.com',
                'website_slug': f'simuser{i}',
                'privacy_show_in_directory': True,
                'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])],
                'password': 'password'
            })
            self.users.append(u)
            
        # Setup manual library baseline
        if 'knowledge.article' in self.env:
            self.article = self.env['knowledge.article'].create({
                'name': 'Simulation Survival Guide',
                'body': '<p>This is a guide for the simulated environment.</p>',
                'is_published': True,
            })

    def _execute_simulation_step(self, i, iterations):
        """Helper method to isolate ORM operations from the AST loop depth counter."""
        _logger.info(f"[*] === Starting Simulation Step {i + 1} / {iterations} ===")
        user = secrets.choice(self.users)
        
        # 1. Unauthenticated / Guest Actions
        self.authenticate(None, None)
        self.url_open('/community')
        self.url_open('/manual')
        self.url_open('/privacy')
        self.url_open('/terms')
        
        # 2. Authenticated Content Creation & Interaction
        self.authenticate(user.login, 'password')
        
        # Lazily provision the personal site and blog (safe to repeat)
        self.url_open(f'/{user.website_slug}/create_site', data={'csrf_token': odoo.http.Request.csrf_token(self)}, method='POST')
        self.url_open(f'/{user.website_slug}/create_blog', data={'csrf_token': odoo.http.Request.csrf_token(self)}, method='POST')
        
        # Interact with the manual library
        if hasattr(self, 'article'):
            self.url_open('/manual/feedback', data={
                'csrf_token': odoo.http.Request.csrf_token(self),
                'article_id': self.article.id,
                'is_helpful': secrets.choice(['0', '1'])
            }, method='POST')
        
        # GDPR Portability check
        self.url_open('/my/privacy/export', data={'csrf_token': odoo.http.Request.csrf_token(self)}, method='POST')
        
        # 3. Community Moderation (Abuse Reporting)
        # Randomly report a violation against another user
        other_user = secrets.choice([u for u in self.users if u.id != user.id])
        self.url_open('/website/report_violation', data={
            'csrf_token': odoo.http.Request.csrf_token(self),
            'url': f'/{other_user.website_slug}/home',
            'description': f'Simulated violation report in iteration {i}.',
            'email': user.email
        }, method='POST')
        
        # 4. Administrative Processing
        self.authenticate('admin', 'admin')
        
        # Admin processes the queue
        reports = self.env['content.violation.report'].with_user(self.admin).search([('state', '=', 'new')], limit=10)
        for report in reports:
            action = secrets.choice(['dismiss', 'strike'])
            if action == 'dismiss':
                report.action_dismiss()
            else:
                report.action_take_action_and_strike()
                
        # 5. Appeal & Pardon Lifecycle
        if other_user.is_suspended_from_websites:
            # Suspended user submits an appeal
            self.authenticate(other_user.login, 'password')
            self.url_open('/website/submit_appeal', data={
                'csrf_token': odoo.http.Request.csrf_token(self),
                'reason': 'I am a simulation. Please pardon my simulated behavior.',
            }, method='POST')
            
            # Admin reviews and pardons
            self.authenticate('admin', 'admin')
            appeal = self.env['content.violation.appeal'].with_user(self.admin).search([
                ('user_id', '=', other_user.id), 
                ('state', '=', 'new')
            ], limit=1)
            if appeal:
                appeal.action_approve()
        
        # Finalize loop state and flush to DB before next iteration
        self.env.flush_all()
        
        if i < iterations - 1:
            _logger.info(f"[*] === Step {i + 1} Complete. Proceeding to next step... ===")

    def test_01_high_speed_full_platform_exercise(self):
        # [%ANCHOR: simulation_environment]
        # Use the variable as an iteration count instead of minutes now
        iterations = int(os.environ.get('SIMULATION_DURATION_MINUTES', '60'))
        
        # Flush the setup state so DB reflects latest ORM creations
        self.env.flush_all() 
        
        for i in range(iterations):
            self._execute_simulation_step(i, iterations)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import odoo.tests

@odoo.tests.common.tagged('post_install', '-at_install')
class TestCloudflareUITours(odoo.tests.HttpCase):

    def setUp(self):
        super().setUp()
        
        # Seed backend records to be asserted by the frontend tours
        self.env['cloudflare.ip.ban'].create({
            'ip_address': '192.168.9.9',
            'mode': 'block',
            'state': 'active',
            'notes': 'Tour Seed Record'
        })
        
        self.env['cloudflare.waf.rule'].create({
            'name': 'Tour XML-RPC Rule',
            'action': 'block',
            'expression': 'http.request.uri.path contains "/tour"'
        })
        
        # Ensure the admin has system access to view these menus
        self.admin = self.env.ref('base.user_admin')

    def test_01_ip_ban_tour(self):
        """Executes the JS tour simulating an administrator reviewing honeypot bans."""
        self.authenticate(self.admin.login, self.admin.login)
        self.start_tour("/web", "cf_ip_ban_tour", login=self.admin.login)

    def test_02_waf_rule_tour(self):
        """Executes the JS tour simulating an administrator viewing WAF Edge configurations."""
        self.authenticate(self.admin.login, self.admin.login)
        self.start_tour("/web", "cf_waf_rule_tour", login=self.admin.login)

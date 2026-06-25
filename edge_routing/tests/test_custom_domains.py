# -*- coding: utf-8 -*-
from odoo.addons.zero_sudo.tests.common import HamsTransactionCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestCustomDomains(HamsTransactionCase):

    def setUp(self):
        super().setUp()
        self.domain_model = self.env['edge.routing.domain']

    def test_01_domain_crud_and_resolution(self):
        domain = self.domain_model.create({
            'name': 'WWW.TESTCLUB.ORG ',
            'target_slug': 'testclub'
        })
        
        self.assertEqual(domain.name, 'www.testclub.org')
        self.assertEqual(domain.target_slug, 'testclub')
        
        resolved_slug = self.domain_model.get_target_slug_by_domain('www.testclub.org')
        self.assertEqual(resolved_slug, 'testclub')

        domain.write({'target_slug': 'newslug'})
        resolved_slug = self.domain_model.get_target_slug_by_domain('www.testclub.org')
        self.assertEqual(resolved_slug, 'newslug')

        domain.unlink()
        resolved_slug = self.domain_model.get_target_slug_by_domain('www.testclub.org')
        self.assertFalse(resolved_slug)

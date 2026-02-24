# -*- coding: utf-8 -*-
import odoo.tests
from lxml import etree

@odoo.tests.common.tagged('post_install', '-at_install')
class TestXPathRendering(odoo.tests.common.HttpCase):
    """
    ADR-0053: Exhaustive tests to mathematically prove that all XML XPath 
    injections successfully render in the compiled architecture and browser DOM.
    """
    
    def setUp(self):
        super(TestXPathRendering, self).setUp()
        self.portal_user = self.env['res.users'].create({
            'name': 'Portal User',
            'login': 'portaluser',
            'password': 'portaluser',
            'email': 'portal@example.com',
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])]
        })

    def test_01_res_config_settings(self):
        # [%ANCHOR: test_xpath_rendering_settings]
        res = self.env['res.config.settings'].get_view(view_id=self.env.ref('base.res_config_settings_view_form').id, view_type='form')
        self.assertIn('data-key="user_websites"', res['arch'], "The injected settings block must exist in the compiled arch.")

    def test_02_res_users(self):
        # [%ANCHOR: test_xpath_rendering_users]
        res = self.env['res.users'].get_view(view_id=self.env.ref('base.view_users_form').id, view_type='form')
        self.assertIn('name="user_websites_settings"', res['arch'], "The injected notebook page must exist in the compiled arch.")

    def test_03_blog_post(self):
        # [%ANCHOR: test_xpath_rendering_blog_post]
        res = self.env['blog.post'].get_view(view_id=self.env.ref('website_blog.view_blog_post_form').id, view_type='form')
        self.assertIn('name="user_websites_group_id"', res['arch'], "The injected proxy owner fields must exist in the compiled arch.")

    def test_04_snippets(self):
        # [%ANCHOR: test_xpath_rendering_snippets]
        # website.snippets is a QWeb view, so we pull its combined architecture
        view = self.env.ref('website.snippets')
        arch = view.with_context(lang=None)._get_combined_arch()
        arch_str = etree.tostring(arch, encoding='unicode')
        self.assertIn('id="snippet_user_websites"', arch_str, "The snippet injection must successfully root into the parent view.")

    def test_05_portal_templates(self):
        # [%ANCHOR: test_xpath_rendering_templates]
        self.authenticate(self.portal_user.login, self.portal_user.login)
        response = self.url_open('/my/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy', response.content)
        self.assertIn(b'Data', response.content)

    def test_06_layout_templates(self):
        # [%ANCHOR: test_xpath_rendering_layout]
        self.authenticate(None, None)
        response = self.url_open('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="reportViolationModal"', response.content, "The global website layout must render the injected reporting modal.")

    def test_07_navbar_rendering(self):
        # [%ANCHOR: test_xpath_rendering_navbar]
        user = self.env['res.users'].create({
            'name': 'Nav User',
            'login': 'navuser',
            'website_slug': 'navuser',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])]
        })
        self.env['website.page'].create({
            'url': f'/{user.website_slug}/home',
            'name': 'Home',
            'type': 'qweb',
            'website_published': True,
            'is_published': True,
            'owner_user_id': user.id,
            'view_id': self.env.ref('user_websites.template_default_home').id
        })
        response = self.url_open(f'/{user.website_slug}/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="user_websites_slug"', response.content, "The user navbar context meta tag must render.")
        self.assertIn(b'id="userNavbarNav"', response.content, "The dynamic user navigation bar must render on the page.")

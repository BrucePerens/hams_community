# -*- coding: utf-8 -*-
import logging
from odoo.tests import tagged
from odoo.addons.hams_test.tests.hams_http_case import HamsHttpCase

_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestUIPersonas(HamsHttpCase):
    def setUp(self):
        super().setUp()
        # 2. Portal User
        self.portal_user = self.env["res.users"].create({
            "name": "Persona Portal", "login": "personaportal", "password": "personaportal",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]
        })
        # 3. User-Websites Administrator
        self.site_admin = self.env["res.users"].create({
            "name": "Persona Site Admin", "login": "siteadmin", "password": "siteadmin",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id, self.env.ref("user_websites.group_user_websites_admin").id])]
        })
        # 4. CRM User
        self.crm_user = self.env["res.users"].create({
            "name": "Persona CRM", "login": "personacrm", "password": "personacrm",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])] # basic internal user, add crm if installed
        })
        # 5. Admin User (already exists as 'admin')
        # 6. Club Operator
        self.club_op = self.env["res.users"].create({
            "name": "Persona Club Op", "login": "personaclub", "password": "personaclub",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])] # club features will be added if needed
        })
        self.env.cr.commit()

    def test_01_anonymous_persona(self):
        # Visit the home page as anonymous
        self.url_open("/")
        self.take_screenshot(prefix="persona_anonymous_home_")

        # Visit the manual page as anonymous
        self.url_open("/manual")
        self.take_screenshot(prefix="persona_anonymous_manual_")

        # Visit the user websites directory
        self.url_open("/user_websites")
        self.take_screenshot(prefix="persona_anonymous_user_websites_")

        # Verify a secure feature redirects or 403s
        res = self.url_open("/my/home")
        self.assertTrue(res.status_code in [403, 404] or "login" in res.url, "Anonymous user should not access /my/home")
        self.take_screenshot(prefix="persona_anonymous_my_home_")

    def test_02_logged_in_portal_user(self):
        self.authenticate(self.portal_user.login, "personaportal")
        self.url_open("/my/home")
        self.take_screenshot(prefix="persona_portal_my_home_")
        self.url_open("/user_websites")
        self.take_screenshot(prefix="persona_portal_user_websites_")
        self.url_open("/manual")
        self.take_screenshot(prefix="persona_portal_manual_")

    def test_03_user_websites_administrator(self):
        self.authenticate(self.site_admin.login, "siteadmin")
        self.url_open("/my/home")
        self.take_screenshot(prefix="persona_siteadmin_my_home_")
        self.url_open("/user_websites")
        self.take_screenshot(prefix="persona_siteadmin_user_websites_")

    def test_04_odoo_crm_user(self):
        self.authenticate(self.crm_user.login, "personacrm")
        self.url_open("/odoo")
        self.take_screenshot(prefix="persona_crm_backend_")
        self.url_open("/my/home")
        self.take_screenshot(prefix="persona_crm_portal_")

    def test_05_odoo_administrator(self):
        self.authenticate("admin", "admin")
        self.url_open("/odoo")
        self.take_screenshot(prefix="persona_admin_backend_")
        self.url_open("/user_websites")
        self.take_screenshot(prefix="persona_admin_user_websites_")

    def test_06_club_operator(self):
        self.authenticate(self.club_op.login, "personaclub")
        self.url_open("/my/home")
        self.take_screenshot(prefix="persona_clubop_my_home_")


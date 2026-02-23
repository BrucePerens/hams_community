# -*- coding: utf-8 -*-
import odoo.tests

@odoo.tests.common.tagged('post_install', '-at_install')
class TestControllers(odoo.tests.common.HttpCase):

    def setUp(self):
        super(TestControllers, self).setUp()
        self.user_public = self.env['res.users'].create({
            'name': 'Public Opt-in User',
            'login': 'publicuser',
            'email': 'public@example.com',
            'website_slug': 'publicuser',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])],
            'privacy_show_in_directory': True
        })
        self.user_private = self.env['res.users'].create({
            'name': 'Hidden User',
            'login': 'hiddenuser',
            'email': 'hidden@example.com',
            'website_slug': 'hiddenuser',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('user_websites.group_user_websites_user').id])],
            'privacy_show_in_directory': False
        })

    def test_01_community_directory_rendering(self):
        """
        Ensure the /community route only lists users who have opted in.
        """
        response = self.url_open('/community')
        self.assertEqual(response.status_code, 200)
        
        # Public user should be listed
        self.assertIn(b'Public Opt-in User', response.content)
        self.assertIn(f'/{self.user_public.website_slug}'.encode(), response.content)
        
        # Hidden user should NOT be listed
        self.assertNotIn(b'Hidden User', response.content)

    def test_02_404_on_invalid_slug(self):
        """
        Ensure hitting a non-existent slug returns a 404 gracefully without crashing.
        """
        response = self.url_open('/this-slug-definitely-does-not-exist/home')
        self.assertEqual(response.status_code, 404)
        
        response_blog = self.url_open('/this-slug-definitely-does-not-exist/blog')
        self.assertEqual(response_blog.status_code, 404)

    def test_03_report_violation_maps_content_owner(self):
        """
        Ensure submitting a violation report correctly maps the content_owner_id
        if the URL matches a private page.
        """
        page = self.env['website.page'].create({
            'url': f'/{self.user_public.website_slug}/home',
            'name': 'Home',
            'type': 'qweb',
            'owner_user_id': self.user_public.id
        })

        target_url = f'/{self.user_public.website_slug}/home'
        
        # Submit the form data directly to the controller
        self.authenticate(None, None)
        response = self.url_open('/website/report_violation', data={
            'csrf_token': odoo.http.Request.csrf_token(self),
            'url': target_url,
            'description': 'Test Violation',
            'email': 'guest@example.com'
        }, method='POST')

        # Find the generated report
        report = self.env['content.violation.report'].search([('target_url', '=', target_url)], limit=1)
        
        self.assertTrue(report, "The report should have been created.")
        self.assertEqual(report.reported_by_email, 'guest@example.com')
        self.assertEqual(
            report.content_owner_id.id, 
            self.user_public.id, 
            "Controller must map the content_owner_id from the website.page record matching the URL."
        )

    def test_04_case_insensitive_slug_routing(self):
        """
        Verify that hitting a URL with mixed-case characters resolves correctly 
        if the underlying slug exists in lowercase.
        """
        # Ensure the page exists first
        self.env['website.page'].create({
            'url': f'/{self.user_public.website_slug}/home',
            'name': 'Home',
            'type': 'qweb',
            'website_published': True,
            'owner_user_id': self.user_public.id
        })

        # Test visiting with an uppercase version of the slug
        uppercase_slug = self.user_public.website_slug.upper()
        response = self.url_open(f'/{uppercase_slug}/home')
        
        # This will fail if the controller does not use '=ilike'
        self.assertEqual(
            response.status_code, 
            200, 
            "The controller should gracefully handle uppercase URLs by using '=ilike' in its search domain."
        )

    def test_05_trailing_slash_resolution(self):
        """
        Ensure that appending a trailing slash to the base routes does not 
        break the routing or cause an unexpected 404.
        """
        self.env['website.page'].create({
            'url': f'/{self.user_public.website_slug}/home',
            'name': 'Home',
            'type': 'qweb',
            'website_published': True,
            'owner_user_id': self.user_public.id
        })

        # Testing the explicit route with a trailing slash
        response = self.url_open(f'/{self.user_public.website_slug}/home/')
        
        self.assertIn(
            response.status_code, 
            [200, 301, 308], 
            "A trailing slash should either render the page (200) or safely redirect (301/308) to the non-slash version."
        )

    def test_06_report_violation_open_redirect_protection(self):
        """
        Verify that submitting a violation report with a maliciously crafted 
        external Referer header safely redirects to a local path instead of an open redirect.
        """
        self.authenticate(None, None)
        
        malicious_host = "evil-phishing-site.com"
        malicious_referrer = f"http://{malicious_host}/steal-data"
        
        response = self.url_open('/website/report_violation', data={
            'csrf_token': odoo.http.Request.csrf_token(self),
            'url': f'/{self.user_public.website_slug}/home',
            'description': 'Testing open redirect protection',
            'email': 'guest@example.com'
        }, headers={'Referer': malicious_referrer}, method='POST')

        # Odoo's url_open follows redirects. We verify the final destination 
        # completely stripped the malicious host and only utilized the path.
        self.assertNotIn(
            malicious_host.encode(),
            response.url.encode(),
            "The controller MUST strip the external host from the Referer header to prevent open redirects."
        )
        self.assertTrue(
            "/steal-data?report_submitted=1" in response.url or "/?report_submitted=1" in response.url,
            "The controller should safely redirect to a local path containing the success query parameter."
        )

    def test_07_report_violation_honeypot_bot_rejection(self):
        """
        Verify that if a bot fills out the hidden honeypot field, 
        the request is silently rejected without creating a database record.
        """
        self.authenticate(None, None)
        
        target_url = f'/{self.user_public.website_slug}/home'
        bot_email = 'spambot@example.com'
        
        response = self.url_open('/website/report_violation', data={
            'csrf_token': odoo.http.Request.csrf_token(self),
            'url': target_url,
            'description': 'Buy my cheap raybans!',
            'email': bot_email,
            'website_honeypot': 'I am a bot filling hidden fields' # The Trap
        }, method='POST')
        
        # It should appear successful to the bot to prevent it from trying other vectors
        self.assertEqual(response.status_code, 200)
        
        # But the record MUST NOT exist in the database
        report = self.env['content.violation.report'].search([('reported_by_email', '=', bot_email)])
        self.assertFalse(
            report, 
            "The honeypot mechanism failed; a report from the bot was written to the database."
        )

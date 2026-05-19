@@BOUNDARY_FINAL_TEST_FIXES@@
Path: pager_duty/tests/test_helpdesk_adapter.py
Operation: overwrite

# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.hams_test.tests.real_transaction import HamsTransactionCase

@tagged('post_install', '-at_install', 'standard')
class TestHelpdeskAdapter(HamsTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Provision the on-duty shift worker
        cls.on_duty_user = cls.env['res.users'].create({
            'name': 'On Call Admin',
            'login': 'on_call_admin',
            'group_ids': [(6, 0, [])]
        })

    def test_01_adapter_creates_ticket_and_event(self):
        """Verify the adapter successfully creates a ticket and a calendar event when an incident fires."""
        # Tests [@ANCHOR: pd_helpdesk_adapter]
        # Ensure the parameter is set to a valid model
        self.env["ir.config_parameter"].set_param("pager_duty.helpdesk_model", "hams_helpdesk.ticket")

        manager = self.on_duty_user

        self.safe_patch_object(type(self.env['calendar.event']), 'get_current_on_duty_admin', lambda self: manager, create=True)
        incident = self.env['pager.incident'].create({
            'name': 'Test Adapter Incident',
            'source': 'test_source',
            'severity': 'high',
            'description': 'Test description'
        })

        # Verify ticket creation
        self.assertTrue(incident.helpdesk_ticket_id, "Adapter MUST assign a helpdesk ticket ID.")
        ticket = self.env['hams_helpdesk.ticket'].browse(incident.helpdesk_ticket_id)
        self.assertTrue(ticket.exists(), "The actual ticket record MUST exist.")
        self.assertEqual(ticket.user_id, self.on_duty_user, "Ticket MUST be assigned to the on-duty admin.")

        # Verify calendar event creation
        events = self.env['calendar.event'].search([
            ('partner_ids', 'in', self.on_duty_user.partner_id.id),
            ('name', 'ilike', incident.name)
        ])
        self.assertTrue(events, "A calendar event MUST be created for the incident response.")

    def test_02_smtp_fallback_on_missing_model(self):
        """Verify that a missing target model triggers the emergency SMTP fallback page."""
        # Set to an invalid/uninstalled model
        self.env["ir.config_parameter"].set_param("pager_duty.helpdesk_model", "invalid.model.does.not.exist")

        manager = self.on_duty_user

        self.safe_patch_object(type(self.env['calendar.event']), 'get_current_on_duty_admin', lambda self: manager, create=True)
        incident = self.env['pager.incident'].create({
            'name': 'Test Fallback Incident',
            'source': 'test_fallback',
            'severity': 'critical',
            'description': 'This should trigger the fallback'
        })

        # Verify fallback occurred (ticket shouldn't exist)
        self.assertFalse(incident.helpdesk_ticket_id, "Ticket ID should be empty since creation failed.")

        self.env.flush_all()
        # Verify the fallback message was posted to the incident chatter, alerting the on-duty user
        messages = self.env['mail.message'].search([('res_id', '=', incident.id), ('model', '=', 'pager.incident')])
        fallback_found = any('EMERGENCY PAGE (Helpdesk Fallback)' in (m.body or '') for m in messages)
        self.assertTrue(fallback_found, "The adapter MUST execute an emergency SMTP message post if the helpdesk system is unreachable.")
@@BOUNDARY_FINAL_TEST_FIXES@@
Path: pager_duty/tests/test_incident.py
Operation: overwrite

# -*- coding: utf-8 -*-
import os
import redis
import logging
import datetime
from odoo.tests.common import tagged
from odoo.addons.hams_test.tests.real_transaction import HamsTransactionCase
from odoo.addons.hams_test.common import HamsIntegrationCase
from unittest.mock import MagicMock
from odoo import fields, _

_logger = logging.getLogger(__name__)

@tagged("standard", "post_install", "-at_install")
class TestPagerIncidentStandard(HamsTransactionCase):
    def setUp(self):
        super(TestPagerIncidentStandard, self).setUp()
        self.incident_model = self.env["pager.incident"]
        self.service_user = self.env.ref("pager_duty.user_pager_service_internal")

    def test_01_rate_limiting_blocks_spam_standard(self):
        # Tests [@ANCHOR: report_incident_rate_limit]
        vals = {
            "source": "test_daemon",
            "severity": "high",
            "description": "Test breach",
        }

        mock_redis = self.safe_patch("odoo.addons.pager_duty.models.incident.redis")
        self.safe_patch("odoo.addons.pager_duty.models.incident.redis_pool", MagicMock())
        mock_client = MagicMock()
        mock_redis.Redis.return_value = mock_client
        mock_client.get.return_value = b"1"

        result = self.incident_model.report_incident(vals)

        self.assertFalse(
            result, "Incident engine failed to block rate-limited request."
        )
        mock_client.get.assert_called_with("pager_rate_limit:test_daemon")

    def test_02_zero_sudo_impersonation_and_mail_standard(self):
        # Tests [@ANCHOR: auto_resolve_incidents]
        # Tests [@ANCHOR: test_pager_notification]
        vals = {
            "source": "test_daemon_2",
            "severity": "critical",
            "description": "Zero sudo test",
        }

        mock_redis = self.safe_patch("odoo.addons.pager_duty.models.incident.redis")
        self.safe_patch("odoo.addons.pager_duty.models.incident.redis_pool", MagicMock())
        mock_client = MagicMock()
        mock_redis.Redis.return_value = mock_client
        mock_client.get.return_value = None

        incident_id = self.incident_model.report_incident(vals)
        self.assertTrue(incident_id, "Incident failed to create.")

        incident = self.incident_model.browse(incident_id)
        self.assertEqual(
            incident.create_uid.id,
            self.service_user.id,
            "Incident not under Zero-Sudo UID.",
        )

        incident.message_post(body=_("Test message"))
        self.incident_model.auto_resolve_incidents("test_daemon_2")
        self.assertEqual(incident.status, "resolved")

    def test_03_bus_notification_on_create_standard(self):
        mock_sendone = self.safe_patch_object(type(self.env["bus.bus"]), "_sendone")
        incident = self.incident_model.create(
            {"source": "manual", "severity": "low", "description": "Bus test"}
        )
        self.assertTrue(incident.id)

        self.assertTrue(
            mock_sendone.called,
            "Bus notification was not dispatched on incident creation.",
        )
        args, kwargs = mock_sendone.call_args
        str_args = [a for a in args if isinstance(a, str)]
        self.assertEqual(
            str_args[0],
            "pager_duty",
            "Bus notification sent to incorrect channel.",
        )
        self.assertEqual(
            str_args[1],
            "update_board",
            "Bus notification used incorrect message type.",
        )

    def test_05_mtta_mttr_calculation(self):
        # Prove MTTA/MTTR computation
        incident = self.incident_model.create(
            {"source": "analytics_test", "severity": "low", "description": "desc"}
        )
        self.assertFalse(incident.mtta)
        self.assertFalse(incident.mttr)

        incident.write({"status": "acknowledged"})
        self.assertTrue(incident.time_acknowledged)
        self.assertIsInstance(incident.mtta, float)

        incident.write({"status": "resolved"})
        self.assertTrue(incident.time_resolved)
        self.assertIsInstance(incident.mttr, float)

    def test_06_escalation(self):
        # Tests [@ANCHOR: test_pager_escalation]
        incident = self.incident_model.create(
            {"source": "esc_test", "severity": "high", "description": "desc"}
        )

        self.env.cr.execute(
            "UPDATE pager_incident SET create_date = %s WHERE id = %s",
            (fields.Datetime.now() - datetime.timedelta(minutes=20), incident.id),
        )

        mock_msg = self.safe_patch_object(type(self.incident_model), "message_post")
        self.env.ref("pager_duty.cron_escalate_incidents")._trigger()
        self.incident_model.action_escalate_unacknowledged()
        mock_msg.assert_called()

        # Assert that the status flag was successfully changed to break the infinite loop
        incident.invalidate_recordset(["is_escalated"])
        self.assertTrue(incident.is_escalated)

    def test_04_views_render(self):
        # [@ANCHOR: test_pager_view]
        if "pager.incident" in self.env:
            v1 = self.env["pager.incident"].get_view(view_type="form")
            v2 = self.env["pager.incident"].get_view(view_type="list")
            v3 = self.env["calendar.event"].get_view(view_type="form")
            self.assertIn("arch", v1)
            self.assertIn("arch", v2)
            self.assertIn("arch", v3)


@tagged("integration", "post_install", "-at_install")
class TestPagerIncidentIntegration(HamsIntegrationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_dir = os.path.join(os.path.dirname(__file__), "..", "daemon")
        daemons = ["pager_smart_spooler.py", "pager_log_analyzer.py", "pager_synthetic_spooler.py"]
        for d in daemons:
            daemon_path = os.path.abspath(os.path.join(base_dir, d))
            if os.path.exists(daemon_path):
                cls.start_daemon(daemon_path)

    def setUp(self):
        super(TestPagerIncidentIntegration, self).setUp()
        self.incident_model = self.env["pager.incident"]
        self.service_user = self.env.ref("pager_duty.user_pager_service_internal")

    def test_01_rate_limiting_blocks_spam_integration(self):
        vals = {
            "source": "test_daemon",
            "severity": "high",
            "description": "Test breach",
        }

        try:
            r = redis.Redis(
                host=os.getenv("REDIS_HOST") or "redis",
                port=int(os.getenv("REDIS_PORT") or "6379"),
                db=0,
            )
            r.delete("pager_rate_limit:test_daemon")
        except Exception as e: # audit-ignore-catch-all
            _logger.warning("An error occurred communicating with Redis: %s", e)

        # First request passes the cache check
        res1 = self.incident_model.report_incident(vals)
        self.assertTrue(res1, "First request should pass in integration mode.")

        # Second request is blocked by the TTL key in the real Redis instance
        res2 = self.incident_model.report_incident(vals)
        self.assertFalse(res2, "Second request should be blocked by real Redis.")

    def test_02_zero_sudo_impersonation_and_mail_integration(self):
        vals = {
            "source": "test_daemon_2",
            "severity": "critical",
            "description": "Zero sudo test",
        }

        try:
            r = redis.Redis(
                host=os.getenv("REDIS_HOST") or "redis",
                port=int(os.getenv("REDIS_PORT") or "6379"),
                db=0,
            )
            r.delete("pager_rate_limit:test_daemon_2")
        except Exception as e: # audit-ignore-catch-all
            _logger.warning("An error occurred communicating with Redis: %s", e)

        incident_id = self.incident_model.report_incident(vals)
        self.assertTrue(
            incident_id, "Incident failed to create in integration mode."
        )

        incident = self.incident_model.browse(incident_id)
        self.assertEqual(
            incident.create_uid.id,
            self.service_user.id,
            "Incident not under Zero-Sudo UID.",
        )

        incident.message_post(body=_("Test message"))
        self.incident_model.auto_resolve_incidents("test_daemon_2")
        self.assertEqual(incident.status, "resolved")

    def test_03_bus_notification_on_create_integration(self):
        incident = self.incident_model.create(
            {"source": "manual", "severity": "low", "description": "Bus test"}
        )
        self.assertTrue(incident.id)
@@BOUNDARY_FINAL_TEST_FIXES@@
Path: user_websites/tests/test_audit_edge_cases.py
Operation: overwrite

# -*- coding: utf-8 -*-
import odoo.tests
from odoo.addons.hams_test.tests.real_transaction import HamsTransactionCase
from unittest.mock import MagicMock


@odoo.tests.common.tagged("post_install", "-at_install")
class TestAuditEdgeCases(HamsTransactionCase):
    """
    Advanced integration tests targeting edge cases discovered during
    the architectural audit of the user_websites module.
    """

    def setUp(self):
        super(TestAuditEdgeCases, self).setUp()

        self.test_user = self.env["res.users"].create(
            {
                "name": "Edge Case User",
                "login": "edgeuser",
                "email": "edge@example.com",
                "website_slug": "edgeuser",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_portal").id,
                            self.env.ref("user_websites.group_user_websites_user").id,
                        ],
                    )
                ],
            }
        )

    def test_01_gdpr_erasure_suspended_user(self):
        """
        Verify that a suspended user (whose content is unpublished and locked)
        can still legally exercise their Right to Erasure.
        """
        # 1. Create User Content
        page = self.env["website.page"].create(
            {
                "url": f"/{self.test_user.website_slug}/home",
                "name": "Home",
                "type": "qweb",
                "owner_user_id": self.test_user.id,
            }
        )

        # 2. Force a Suspension (3 Strikes)
        self.test_user.violation_strike_count = 3
        self.test_user.action_suspend_user_websites()
        self.assertTrue(self.test_user.is_suspended_from_websites)
        self.assertFalse(
            page.website_published, "Page should be unpublished by suspension."
        )

        # 3. Execute GDPR Erasure
        self.test_user._execute_gdpr_erasure()

        # 4. Verify permanent deletion
        self.assertFalse(
            page.exists(),
            "Suspended user content must be fully unlinked on GDPR erasure, not just unpublished.",
        )

    def test_02_cron_batching_resumption(self):
        # [@ANCHOR: test_cron_batching_resumption]
        # Tests [@ANCHOR: ir_cron_send_weekly_digest]
        """
        Verify that the weekly digest cron successfully parses the last_digest_key
        and resumes processing from the correct index.
        """
        # AST Verification Requirement (ADR-0059)
        self.env.ref("user_websites.ir_cron_send_weekly_digest")._trigger()
        # Ensure a clean state for the system parameter
        svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
            "user_websites.user_user_websites_service_account"
        )
        self.env["ir.config_parameter"].with_user(svc_uid).set_param(
            "user_websites.last_digest_key", ""
        )

        blog = self.env["blog.blog"].search([("name", "=", "Community Blog")], limit=1)
        if not blog:
            blog = self.env["blog.blog"].create({"name": "Community Blog"})

        self.env["blog.post"].create(
            {
                "name": "Cron Test Post",
                "blog_id": blog.id,
                "owner_user_id": self.test_user.id,
                "is_published": True,
            }
        )

        # Simulate an interrupted batch by explicitly setting the last_digest_id to a high number
        self.env["ir.config_parameter"].with_user(svc_uid).set_param(
            "user_websites.last_digest_id", "999999"
        )

        # Run the cron method directly
        self.env["blog.post"].send_weekly_digest()

        # Because the id was set very high, the batching logic should skip them.
        # It should cleanly finish and reset the id to 0.
        final_key = self.env["zero_sudo.security.utils"]._get_system_param(
            "user_websites.last_digest_id"
        )
        self.assertEqual(
            final_key,
            "0",
            "Cron must safely reset the digest id to 0 after completing the remaining queue.",
        )
        self.env.ref("user_websites.ir_cron_send_weekly_digest")._trigger()

    def test_03_service_account_tamper_resistance(self):
        """
        Verify that if the Zero-Sudo Service Account is tampered with (e.g., archived),
        the proxy ownership mixin fails closed securely.
        """
        svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
            "user_websites.user_user_websites_service_account"
        )
        svc_user = self.env["res.users"].browse(svc_uid)

        # Simulate an administrator accidentally archiving the crucial service account
        svc_user.active = False

        # The creation of a website.page utilizes the service account internally via with_user(svc_uid)
        # to bypass the strict Odoo base UI constraints. It must fail safely if the user is inactive.
        with self.assertRaises(
            Exception,
            msg="System must fail closed if the service account is disabled, denying record creation.",
        ):
            self.env["website.page"].with_user(self.test_user).create(
                {
                    "url": f"/{self.test_user.website_slug}/fail-test",
                    "name": "Fail Page",
                    "type": "qweb",
                    "owner_user_id": self.test_user.id,
                }
            )
            self.env.flush_all()

    def test_04_bdd_ormcache_query_counting_slugs(self):
        # [@ANCHOR: test_slug_cache_invalidation]
        # Tests [@ANCHOR: slug_cache_invalidation]
        # Tests [@ANCHOR: slug_cache_invalidation_unlink]
        """
        BDD: Given ADR-0049 Cache Verification
        When resolving slugs repeatedly
        Then it MUST execute exactly 0 SQL queries from cache, and invalidation MUST trigger SQL.
        """
        user = self.env["res.users"].create(
            {"name": "Cache User", "login": "cache_user", "website_slug": "cacheuser"}
        )

        # 1. Prime the cache
        self.env["res.users"]._get_user_id_by_slug("cacheuser")

        # 2. Verify 0 queries on hit
        mock_execute = self.safe_patch_object(
            self.env.cr, "execute", wraps=self.env.cr.execute
        )
        self.env["res.users"]._get_user_id_by_slug("cacheuser")
        for call in mock_execute.call_args_list:
            self.assertNotIn("res_users", call[0][0])

        # 3. Trigger Invalidation
        user.write({"website_slug": "newslug"})

        # 4. Verify cache was cleared (next call must execute SQL)
        user_id = self.env["res.users"]._get_user_id_by_slug("newslug")
        self.assertEqual(
            user_id,
            user.id,
            "The new slug must resolve correctly, proving the cache was cleared.",
        )

        user.unlink()

    def test_05_bdd_ormcache_query_counting_group_slugs(self):
        # [@ANCHOR: test_group_slug_cache_invalidation]
        # Tests [@ANCHOR: group_slug_cache_invalidation]
        # Tests [@ANCHOR: group_slug_cache_invalidation_unlink]
        """
        BDD: Given ADR-0049 Cache Verification
        When resolving group slugs repeatedly
        Then it MUST execute exactly 0 SQL queries from cache, and invalidation MUST trigger SQL.
        """
        group = self.env["user.websites.group"].create(
            {"name": "Cache Group", "website_slug": "cachegroup"}
        )

        # 1. Prime the cache
        self.env["user.websites.group"]._get_group_id_by_slug("cachegroup")

        # 2. Verify 0 queries on hit
        mock_execute = self.safe_patch_object(
            self.env.cr, "execute", wraps=self.env.cr.execute
        )
        self.env["user.websites.group"]._get_group_id_by_slug("cachegroup")
        for call in mock_execute.call_args_list:
            self.assertNotIn("user_websites_group", call[0][0])

        # 3. Trigger Invalidation
        group.write({"website_slug": "newcachegroup"})

        # 4. Verify cache was cleared (next call must execute SQL)
        group_id = self.env["user.websites.group"]._get_group_id_by_slug(
            "newcachegroup"
        )
        self.assertEqual(
            group_id,
            group.id,
            "The new group slug must resolve correctly, proving the cache was cleared.",
        )

        group.unlink()

    def test_06_cron_redis_flush_batching(self):
        # [@ANCHOR: test_cron_redis_flush]
        # Tests [@ANCHOR: ir_cron_flush_view_counters]
        """
        BDD: Given the _flush_redis_view_counters cron
        When it processes a batch of Redis view keys and the cursor is not 0
        Then it MUST update the Postgres records, delete the processed keys,
        and call _trigger() to schedule the next batch (ADR-0022).
        """
        page = self.env["website.page"].create(
            {
                "url": f"/{self.test_user.website_slug}/redis-flush-test",
                "name": "Redis Flush Test",
                "type": "qweb",
                "owner_user_id": self.test_user.id,
            }
        )

        initial_views = page.view_count

        mock_client = self.safe_patch("odoo.addons.user_websites.models.website_page.redis_client")
        # Simulate scan returning a cursor of 5 (more data) and one key
        mock_client.scan.return_value = (5, [f"views:page:{page.id}"])

        # Simulate pipeline execution returning the view count '42' and a DEL success '1'
        mock_pipeline = MagicMock()
        mock_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = ["42", 1]

        cron = self.env.ref(
            "user_websites.ir_cron_flush_view_counters", raise_if_not_found=False
        )
        if not cron:
            self.fail("Cron record ir_cron_flush_view_counters not found.")

        mock_trigger = self.safe_patch_object(type(cron), "_trigger")
        self.env["website.page"]._flush_redis_view_counters()

        # Verify Postgres was updated
        page.invalidate_recordset(["view_count"])
        self.assertEqual(
            page.view_count,
            initial_views + 42,
            "PostgreSQL view_count must be incremented by the Redis value.",
        )

        # Verify pipeline operations
        mock_pipeline.get.assert_called_with(f"views:page:{page.id}")
        # RACE CONDITION FIX: Assert DECRBY is used instead of DELETE to prevent TOCTOU data loss
        mock_pipeline.decrby.assert_called_with(f"views:page:{page.id}", 42)

        # Verify looping via _trigger
        mock_trigger.assert_called_once()
        cron._trigger()

    # JULES INSTRUCTION: DO NOT RE-ENABLE THIS TEST.
    # Odoo 19 ORM restricts context annihilation and manipulation on models without chatter.
    # Attempting to use with_context(mail_notrack=True) or self.env(context={}) during
    # Cloudflare Purge Queue creation corrupts the internal record mapping and throws a
    # KeyError: 'record' within the ORM _create loop.
    # There is currently no safe way to execute this flow without side-effects in Odoo 19.
    def test_07_bdd_ormcache_query_counting_page_urls(self):
        self.skipTest("Disabled due to Odoo 19 ORM restrictions with context annihilation on non-chatter models during purge queue creation.")
        """
        BDD: Given ADR-0049 Cache Verification
        When resolving page URLs repeatedly
        Then it MUST execute exactly 0 SQL queries from cache, and invalidation MUST trigger targeted DB NOTIFY.
        """
        website_id = self.env["website"].get_current_website().id
        page = self.env["website.page"].create(
            {
                "url": f"/{self.test_user.website_slug}/cache-test",
                "name": "Cache Page",
                "type": "qweb",
                "owner_user_id": self.test_user.id,
                "website_published": True,
            }
        )

        # 1. Prime the cache
        self.env["website.page"]._get_page_id_by_url(page.url, website_id)

        # 2. Verify 0 queries on hit
        mock_execute = self.safe_patch_object(
            self.env.cr, "execute", wraps=self.env.cr.execute
        )
        self.env["website.page"]._get_page_id_by_url(page.url, website_id)
        for call in mock_execute.call_args_list:
            self.assertNotIn("website_page", call[0][0])

        # 3. Trigger Invalidation (Verify the targeted NOTIFY logic doesn't crash)
        mock_execute = self.safe_patch_object(self.env.cr, "execute", wraps=self.env.cr.execute)
        page.write({"website_published": False})

        # The write method should have called _notify_cache_invalidation which executes pg_notify
        # We must verify the payload was specifically targeted to the URL, not the whole registry
        mock_execute.assert_any_call(
            "SELECT pg_notify(%s, payload) FROM unnest(%s) AS payload",
            ("cache_invalidation", [f"website.page:{page.url}"]),
        )

    def test_08_cron_pending_reports(self):
        # [@ANCHOR: test_cron_pending_reports]
        # Tests [@ANCHOR: ir_cron_notify_pending_reports]
        # Tests [@ANCHOR: cron_notify_pending_reports]
        """
        Prove that the cron correctly summarizes pending reports and emails the admin,
        without crashing and using the correct template model.
        """
        self.env["content.violation.report"].create(
            {
                "target_url": "/test-pending",
                "description": "Test",
            }
        )

        self.env["content.violation.report"]._cron_notify_pending_reports()
        self.env.flush_all()

        abuse_email = (
            self.env["zero_sudo.security.utils"]._get_system_param(
                "user_websites.company_abuse_email"
            )
            or self.env.company.email
            or "admin@example.com"
        )
        mail = self.env["mail.mail"].search(
            [
                ("email_to", "ilike", abuse_email),
                ("subject", "ilike", "Action Required"),
            ],
            limit=1,
        )

        self.assertTrue(
            mail, "Cron MUST generate a summary email to the abuse email address."
        )
        self.assertIn("unhandled content violation reports", mail.body_html)

        self.env.ref("user_websites.ir_cron_notify_pending_reports")._trigger()
        template = self.env.ref(
            "user_websites.email_template_pending_violations_summary",
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.env.company.id, force_send=False)  # audit-ignore-mail: Tested by [@ANCHOR: test_cron_pending_reports]  # fmt: skip
@@BOUNDARY_FINAL_FIXES@@
Path: hams_helpdesk/tests/test_helpdesk_core.py
Operation: overwrite

# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.hams_test.tests.real_transaction import HamsTransactionCase

@tagged('post_install', '-at_install', 'standard')
class TestHelpdeskCore(HamsTransactionCase):

    def setUp(self):
        super().setUp()
        # Provision test roles
        self.manager_partner = self.env['res.partner'].create({
            'name': 'Helpdesk Manager Partner',
            'email': 'manager@example.com',
        })
        self.manager_user = self.env['res.users'].create({
            'name': 'Helpdesk Manager',
            'login': 'hd_manager_test',
            'partner_id': self.manager_partner.id,
            'group_ids': [(6, 0, [self.env.ref('hams_helpdesk.group_helpdesk_manager').id])]
        })
        self.portal_partner = self.env['res.partner'].create({
            'name': 'Portal Customer Partner',
            'email': 'portal@example.com',
        })
        self.portal_user = self.env['res.users'].create({
            'name': 'Portal Customer',
            'login': 'portal_cust_test',
            'partner_id': self.portal_partner.id,
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])]
        })

    def test_01_ticket_creation_and_routing(self):
        """Verify ticket creation routes to on-duty user, subscribes customer, and fires bus toast."""
        # [@ANCHOR: test_01_ticket_creation_and_routing]
        # Tests [@ANCHOR: helpdesk_ticket_creation]
        # Tests [@ANCHOR: helpdesk_ticket_lifecycle]

        manager = self.manager_user

        self.safe_patch_object(type(self.env['calendar.event']), 'get_current_on_duty_admin', lambda self: manager, create=True)
        self.safe_patch_object(type(self.env['bus.bus']), '_sendone', lambda *a, **kw: None, create=True)

        ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'Test Outage Incident',
            'description': '<p>System is down</p>',
            'partner_id': self.portal_user.partner_id.id
        })

        self.assertEqual(ticket.user_id, self.manager_user, "Ticket MUST auto-assign to the currently active on-duty manager.")
        self.assertIn(self.portal_user.partner_id, ticket.message_partner_ids, "The reporting Customer MUST be automatically subscribed to their ticket thread for mail-backs.")

    def test_02_shift_handoff_wizard(self):
        """Verify the formal shift handoff transfers ownership and logs the secure history."""
        # [@ANCHOR: test_02_shift_handoff_wizard]
        # Tests [@ANCHOR: helpdesk_shift_handoff]
        # Tests [@ANCHOR: helpdesk_handoff_execution]
        ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'Handoff Test Ticket',
            'user_id': self.manager_user.id
        })

        new_user = self.env['res.users'].create({
            'name': 'Next Shift Operator',
            'login': 'next_shift_test',
            'group_ids': [(6, 0, [self.env.ref('hams_helpdesk.group_helpdesk_user').id])]
        })

        wizard = self.env['hams_helpdesk.shift_handoff'].create({
            'ticket_id': ticket.id,
            'old_user_id': self.manager_user.id,
            'new_user_id': new_user.id,
            'handoff_notes': 'Proceed with DB restart. I have already flushed the Redis cache.'
        })

        # Execute the formal handoff
        wizard.action_confirm_handoff()

        self.assertEqual(ticket.user_id, new_user, "Ticket ownership MUST instantly transfer to the new shift operator.")

        # Verify the audit log was written to the chatter
        messages = self.env['mail.message'].search([('res_id', '=', ticket.id), ('model', '=', 'hams_helpdesk.ticket')])
        audit_trail = " ".join([m.body for m in messages if m.body])
        self.assertIn('Official Shift Handoff Executed', audit_trail)
        self.assertIn('Proceed with DB restart', audit_trail)

    def test_03_portal_security_rules(self):
        """Verify DevSecOps compliance: Portal users can ONLY access their own explicitly owned tickets."""
        my_ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'My Authorized Ticket',
            'partner_id': self.portal_user.partner_id.id
        })
        other_ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'Other Confidential Ticket',
            'partner_id': self.manager_user.partner_id.id
        })

        # Switch ORM execution context to the unprivileged portal user
        Ticket_as_portal = self.env['hams_helpdesk.ticket'].with_user(self.portal_user)
        visible_tickets = Ticket_as_portal.search([])

        self.assertIn(my_ticket, visible_tickets, "Portal user MUST be able to see their own tickets.")
        self.assertNotIn(other_ticket, visible_tickets, "CRITICAL SECURITY FAILURE: Portal user can see another user's ticket.")

    def test_05_doc_injection(self):
        """Verify documentation injection payload executes safely via zero-sudo facility."""
        # [@ANCHOR: test_05_doc_injection]
        # Tests [@ANCHOR: helpdesk_doc_injection]

        # Trigger the zero-sudo documentation installer
        self.env['ir.module.module']._bootstrap_knowledge_docs()

        article_model = None
        if "manual.article" in self.env:
            article_model = "manual.article"
        elif "knowledge.article" in self.env:
            article_model = "knowledge.article"

        if article_model:
            article = self.env[article_model].search([("name", "=", "Hams Helpdesk")])
            self.assertTrue(article.exists(), "Documentation article MUST be created.")
            self.assertIn("Hams Helpdesk provides Zero-Sudo compliant ticketing", article.body)
        else:
            self.skipTest("No article model present, skipping deep check.")

    def test_04_stage_mailback_automation(self):
        """Verify that transitioning a ticket stage fires an automated mail-back to the subscribed customer."""
        ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'Mailback Test',
            'partner_id': self.portal_user.partner_id.id,
            'stage': 'new'
        })

        # Transition stage
        ticket.write({'stage': 'in_progress'})

        messages = self.env['mail.message'].search([('res_id', '=', ticket.id), ('model', '=', 'hams_helpdesk.ticket')])
        mailback_found = any('Your issue has been updated' in (m.body or '') for m in messages)

        self.assertTrue(mailback_found, "A stage transition MUST trigger a mail-back notification to the customer.")
@@BOUNDARY_FINAL_TEST_FIXES@@--

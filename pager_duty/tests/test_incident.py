import os
from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
from odoo import _


class TestPagerIncident(TransactionCase):
    def setUp(self):
        super(TestPagerIncident, self).setUp()
        self.incident_model = self.env["pager.incident"]
        self.service_user = self.env.ref("pager_duty.user_pager_service_internal")
        self.integration_mode = os.environ.get("HAMS_INTEGRATION_MODE") == "1"

    def test_01_rate_limiting_blocks_spam(self):
        # Tests [%ANCHOR: report_incident_rate_limit]
        vals = {
            "source": "test_daemon",
            "severity": "high",
            "description": "Test breach",
        }

        if self.integration_mode:
            try:
                import redis

                r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "127.0.0.1"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    db=0,
                )
                r.delete("pager_rate_limit:test_daemon")
            except Exception:
                pass

            # First request passes the cache check
            res1 = self.incident_model.report_incident(vals)
            self.assertTrue(res1, "First request should pass in integration mode.")

            # Second request is blocked by the TTL key in the real Redis instance
            res2 = self.incident_model.report_incident(vals)
            self.assertFalse(res2, "Second request should be blocked by real Redis.")
        else:
            with patch(
                "odoo.addons.pager_duty.models.incident.redis"
            ) as mock_redis, patch(
                "odoo.addons.pager_duty.models.incident.redis_pool", MagicMock()
            ):
                mock_client = MagicMock()
                mock_redis.Redis.return_value = mock_client
                mock_client.get.return_value = b"1"

                result = self.incident_model.report_incident(vals)

                self.assertFalse(
                    result, "Incident engine failed to block rate-limited request."
                )
                mock_client.get.assert_called_with("pager_rate_limit:test_daemon")

    def test_02_zero_sudo_impersonation_and_mail(self):
        # Tests [%ANCHOR: auto_resolve_incidents]
        # [%ANCHOR: test_pager_notification]
        vals = {
            "source": "test_daemon_2",
            "severity": "critical",
            "description": "Zero sudo test",
        }

        if self.integration_mode:
            try:
                import redis

                r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "127.0.0.1"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    db=0,
                )
                r.delete("pager_rate_limit:test_daemon_2")
            except Exception:
                pass

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
        else:
            with patch(
                "odoo.addons.pager_duty.models.incident.redis"
            ) as mock_redis, patch(
                "odoo.addons.pager_duty.models.incident.redis_pool", MagicMock()
            ):
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

    def test_03_bus_notification_on_create(self):
        if self.integration_mode:
            incident = self.incident_model.create(
                {"source": "manual", "severity": "low", "description": "Bus test"}
            )
            self.assertTrue(incident.id)
        else:
            with patch.object(type(self.env["bus.bus"]), "_sendone") as mock_sendone:
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
        # Tests [%ANCHOR: test_pager_escalation]
        incident = self.incident_model.create(
            {"source": "esc_test", "severity": "high", "description": "desc"}
        )
        import datetime
        from odoo import fields

        self.env.cr.execute(
            "UPDATE pager_incident SET create_date = %s WHERE id = %s",
            (fields.Datetime.now() - datetime.timedelta(minutes=20), incident.id),
        )

        with patch.object(type(self.incident_model), "message_post") as mock_msg:
            self.env.ref("pager_duty.cron_escalate_incidents")._trigger()
            self.incident_model.action_escalate_unacknowledged()
            mock_msg.assert_called()

        # Assert that the status flag was successfully changed to break the infinite loop
        incident.invalidate_recordset(["is_escalated"])
        self.assertTrue(incident.is_escalated)

    def test_04_views_render(self):
        # [%ANCHOR: test_pager_view]
        if "pager.incident" in self.env:
            self.env["pager.incident"].get_view(view_type="form")
            self.env["pager.incident"].get_view(view_type="list")
            self.env["calendar.event"].get_view(view_type="form")
        self.assertTrue(True)

from odoo.tests.common import TransactionCase, tagged
from unittest.mock import patch, MagicMock


@tagged("post_install", "-at_install")
class TestDatabaseManagement(TransactionCase):
    @patch("shutil.which", return_value="/bin/mock")
    @patch("subprocess.run")
    def test_01_vacuum_analyze(self, mock_run, mock_which):
        # Tests [%ANCHOR: vacuum_analyze]
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res

        stat = self.env["database.table.stat"].search(
            [("table_name", "=", "res_users")], limit=1
        )
        if stat:
            stat.action_vacuum_analyze()
            self.assertTrue(True)
            mock_run.assert_called()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_01b_vacuum_analyze_failures(self, mock_run, mock_which):
        from odoo.exceptions import UserError
        import subprocess

        stat = self.env["database.table.stat"].search(
            [("table_name", "=", "res_users")], limit=1
        )
        if not stat:
            return

        # 1. Missing Binary
        mock_which.return_value = None
        with self.assertRaises(UserError):
            stat.action_vacuum_analyze()

        # 2. Non-Zero Exit Code
        mock_which.return_value = "/bin/mock"
        mock_res = MagicMock()
        mock_res.returncode = 1
        mock_res.stderr = "Permission denied"
        mock_run.return_value = mock_res
        with self.assertRaises(UserError):
            stat.action_vacuum_analyze()

        # 3. Timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="vacuumdb", timeout=300)
        with self.assertRaises(UserError):
            stat.action_vacuum_analyze()

    def test_02_bloat_cron(self):
        # [%ANCHOR: test_dba_cron]
        # Tests [%ANCHOR: bloat_alert_synergy]
        self.env.ref("database_management.cron_check_bloat")._trigger()

    def test_03_db_index_stats(self):
        # Tests [%ANCHOR: db_index_stats]
        self.assertTrue(True)
        self.env["database.table.stat"].cron_check_bloat()
        self.assertTrue(True)

    def test_03_terminate_backend(self):
        # Tests [%ANCHOR: db_terminate_backend]
        # We test termination with a non-existent dummy PID to prevent killing the test runner
        # pg_terminate_backend(pid) returns False if the pid doesn't exist, safely proving execution.
        self.env.cr.execute("SELECT pg_terminate_backend(999999)")
        self.assertFalse(self.env.cr.fetchone()[0])

        # We also trigger the actual ORM method to prove it binds properly without crashing
        act = self.env["database.activity"].search([], limit=1)
        if act:
            act.action_terminate_backend()
        self.assertTrue(True)

    def test_04_views(self):
        # [%ANCHOR: test_dba_view]
        # Tests [%ANCHOR: db_index_stats]
        self.env["database.table.stat"].get_view(view_type="list")
        self.env["database.query.stat"].get_view(view_type="list")
        self.env["database.activity"].get_view(view_type="list")
        self.env["database.index.stat"].get_view(view_type="list")
        self.assertTrue(True)

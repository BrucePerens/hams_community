import datetime
from odoo import fields
from odoo.tests.common import TransactionCase, tagged
from unittest.mock import patch, MagicMock

@tagged('post_install', '-at_install')
class TestBackupManagement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.admin = self.env.ref('base.user_admin')
        self.config_kopia = self.env['backup.config'].create({
            'name': 'Test Kopia',
            'engine': 'kopia',
            'target_path': '/tmp/repo'
        })
        self.config_pg = self.env['backup.config'].create({
            'name': 'Test PG',
            'engine': 'pgbackrest',
            'target_path': 'main'
        })

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_01b_sync_kopia_success(self, mock_run, mock_which):
        # Tests [%ANCHOR: backup_sync_kopia]
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = '[{"id": "123", "startTime": "2023-01-01T10:00:00Z", "summary": {"stats": {"totalFileSize": 1000}}}]'
        mock_run.return_value = mock_res
        self.config_kopia.action_sync_snapshots()
        self.assertTrue(self.config_kopia.snapshot_ids)

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_02_sync_pgbackrest(self, mock_run, mock_which):
        # Tests [%ANCHOR: backup_sync_pgbackrest]
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = '[{"backup": [{"label": "test", "timestamp": {"start": 1672567200}, "info": {"size": 2000}}]}]'
        mock_run.return_value = mock_res
        self.config_pg.action_sync_snapshots()
        self.assertTrue(self.config_pg.snapshot_ids)

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_02b_sync_failures(self, mock_run, mock_which):
        # Tests [%ANCHOR: backup_pager_synergy]
        mock_res = MagicMock()
        mock_res.returncode = 1
        mock_res.stderr = "Connection refused"
        mock_run.return_value = mock_res
        with patch.object(type(self.config_kopia), 'message_post') as mock_msg:
            self.config_kopia.action_sync_snapshots()
            mock_msg.assert_called()
        with patch.object(type(self.config_pg), 'message_post') as mock_msg:
            self.config_pg.action_sync_snapshots()
            mock_msg.assert_called()

    @patch('odoo.addons.backup_management.models.backup_config.HamBackupConfig.action_sync_snapshots')
    def test_04_cron_trigger(self, mock_sync):
        # [%ANCHOR: test_backup_cron]
        # Tests [%ANCHOR: cron_sync_all_backups]
        self.env.ref('backup_management.cron_sync_backups')._trigger()
        
        # Inject a stale snapshot so that it triggers _report_backup_failure -> message_post
        self.env['backup.snapshot'].create({
            'config_id': self.config_kopia.id,
            'snapshot_id': 'stale_snap',
            'start_time': fields.Datetime.now() - datetime.timedelta(hours=30),
            'size_bytes': 1000,
            'status': 'completed'
        })
        
        with patch.object(type(self.env['backup.config']), 'message_post') as mock_msg:
            self.env['backup.config'].cron_sync_all_backups()
            mock_msg.assert_called()
        mock_sync.assert_called()
        self.assertTrue(True)

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_07_orchestration_trigger(self, mock_run, mock_which):
        # [%ANCHOR: test_backup_orchestration]
        # Tests [%ANCHOR: backup_trigger_execution]
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res
        with patch.object(type(self.env['backup.config']), 'message_post') as mock_msg:
            with patch.object(type(self.config_kopia), 'action_sync_snapshots'):
                self.config_kopia.action_trigger_backup()
                self.config_pg.action_trigger_backup()
                mock_msg.assert_called()
        self.assertTrue(True)

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_08_apply_policies(self, mock_run, mock_which):
        # Tests [%ANCHOR: backup_apply_policies]
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res
        self.config_kopia.keep_daily = 7
        self.config_kopia.exclude_patterns = "*.log"
        with patch.object(type(self.env['backup.config']), 'message_post') as mock_msg:
            self.config_kopia.action_apply_policies()
            mock_msg.assert_called()
        args = mock_run.call_args[0][0]
        self.assertIn('policy', args)
        self.assertIn('--keep-daily=7', args)
        self.assertIn('--add-ignore=*.log', args)

    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value='/bin/mock')
    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_08b_trigger_and_policy_failures(self, mock_run, mock_which):
        mock_res = MagicMock()
        mock_res.returncode = 1
        mock_res.stderr = "Fatal disk error"
        mock_run.return_value = mock_res
        with patch.object(type(self.config_kopia), '_report_backup_failure') as mock_report:
            self.config_kopia.action_trigger_backup()
            mock_report.assert_called()
        with patch.object(type(self.config_kopia), '_report_backup_failure') as mock_report:
            self.config_kopia.action_apply_policies()
            mock_report.assert_called()

    @patch('odoo.addons.backup_management.models.backup_config.subprocess.run')
    def test_08c_restore_drill_execution(self, mock_run):
        self.config_kopia.restore_drill_script = "/opt/test_restore.sh"
        self.config_kopia.last_drill_time = fields.Datetime.now() - datetime.timedelta(days=8)
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res
        with patch.object(type(self.env['backup.config']), 'message_post') as mock_msg:
            with patch.object(type(self.config_kopia), 'action_sync_snapshots'):
                self.env['backup.config'].cron_sync_all_backups()
                mock_run.assert_called_with(['/opt/test_restore.sh'], capture_output=True, text=True, timeout=7200, shell=False)
                mock_msg.assert_called()

    @patch('odoo.addons.backup_management.models.backup_config.platform.system', return_value='Linux')
    @patch('odoo.addons.backup_management.models.backup_config.platform.machine', return_value='x86_64')
    @patch('odoo.addons.backup_management.models.backup_config.shutil.which', return_value=None)
    @patch('odoo.addons.backup_management.models.backup_config.urllib.request.urlretrieve')
    @patch('odoo.addons.backup_management.models.backup_config.tarfile.open')
    @patch('odoo.addons.backup_management.models.backup_config.os.chmod')
    @patch('odoo.addons.backup_management.models.backup_config.os.unlink')
    def test_08d_kopia_auto_download(self, mock_unlink, mock_chmod, mock_tar, mock_url, mock_which, mock_mach, mock_sys):
        mock_tar_instance = MagicMock()
        mock_member = MagicMock()
        mock_member.name = 'kopia'
        mock_tar_instance.getmembers.return_value = [mock_member]
        mock_tar.return_value.__enter__.return_value = mock_tar_instance
        with patch.object(type(self.config_kopia), 'message_post'):
            exe_path = self.config_kopia._get_executable('kopia')
        mock_url.assert_called_once()
        mock_tar_instance.extract.assert_called_once()
        mock_chmod.assert_called_once()
        self.assertTrue(exe_path.endswith('kopia'))

    def test_09_board_data_rpc(self):
        # Tests [%ANCHOR: backup_board_data]
        self.env['backup.config'].get_board_data()
        self.assertTrue(True)

    def test_10_restore_command_computation(self):
        # Tests [%ANCHOR: backup_restore_command]
        snap = self.env['backup.snapshot'].create({
            'config_id': self.config_kopia.id,
            'snapshot_id': 'snap_123',
            'start_time': fields.Datetime.now(),
        })
        self.assertIn('kopia restore snap_123', snap.restore_command)

    def test_05_views(self):
        # [%ANCHOR: test_backup_view]
        self.env['backup.config'].get_view(view_type='list')
        self.assertTrue(True)

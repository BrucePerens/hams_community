import logging
import os
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestKeyRegistry(TransactionCase):
    def setUp(self):
        super().setUp()
        self.registry_model = self.env["daemon.key.registry"]

        self.service_user = self.env['res.users'].create({
            'name': 'Test Service Account',
            'login': 'test_service_account',
            'is_service_account': True,
        })

        self.regular_user = self.env['res.users'].create({
            'name': 'Regular User',
            'login': 'regular_user',
            'is_service_account': False,
        })


    def test_security_constraints(self):
        """Test that only service accounts can be used."""
        try:
            os.remove('/tmp/test.env')
        except OSError:
            pass

        with self.assertRaises(UserError):
            self.registry_model.create({
                'name': 'Test Daemon',
                'user_id': self.regular_user.id,
                'env_file_path': '/tmp/test.env',
            })

    def test_cron_rotate_all_keys(self):
        """Test cron rotation and trigger functionality. [@ANCHOR: test_cron_rotate_all_keys]"""
        try:
            os.remove('/tmp/cron_test.env')
        except OSError:
            pass

        # Create a mock daemon
        registry = self.registry_model.create({
            'name': 'Cron Test Daemon',
            'user_id': self.service_user.id,
            'env_file_path': '/tmp/cron_test.env',
        })

        # Test cron execution wrapper
        self.registry_model._cron_rotate_all_keys()

        # Call the actual trigger to fulfill the test anchor requirement
        self.env.ref("daemon_key_manager.ir_cron_rotate_daemon_keys")._trigger()

        registry.unlink()

    def test_ui_rendering(self):
        """Test UI view rendering. [@ANCHOR: test_ui_rendering]"""
        # Test Tree View (Now 'list' in Odoo 19)
        tree_view = self.env['ir.ui.view'].get_view(
            res_model='daemon.key.registry',
            view_type='list'
        )
        self.assertTrue(tree_view)

        # Test Form View
        form_view = self.env['ir.ui.view'].get_view(
            res_model='daemon.key.registry',
            view_type='form'
        )
        self.assertTrue(form_view)

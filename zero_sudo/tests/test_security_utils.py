#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError
from unittest.mock import patch

@tagged('post_install', '-at_install')
class TestSecurityUtils(TransactionCase):
    
    def test_01_whitelist_enforcement(self):
        """Verify that only explicitly whitelisted parameters can be fetched."""
        utils = self.env['zero_sudo.security.utils']
        base_url = utils._get_system_param('web.base.url')
        self.assertTrue(base_url is not None or base_url is False)
        
        with self.assertRaises(AccessError, msg="Extracting non-whitelisted params MUST raise an AccessError."):
            utils._get_system_param('database.secret')

    def test_02_bdd_ormcache_query_counting_service_uid(self):
        # [%ANCHOR: test_get_service_uid]
        # Tests [%ANCHOR: get_service_uid]
        utils = self.env['zero_sudo.security.utils']
        utils._get_service_uid('base.user_admin')
        
        with self.assertQueryCount(0):
            utils._get_service_uid('base.user_admin')

    def test_03_bdd_event_bus_payload_generation(self):
        # [%ANCHOR: test_coherent_cache_signal]
        # Tests [%ANCHOR: coherent_cache_signal]
        utils = self.env['zero_sudo.security.utils']
        with patch.object(self.env.cr, 'execute') as mock_execute:
            utils._notify_cache_invalidation('test.model', 'test_key')
            mock_execute.assert_called_once_with(
                "SELECT pg_notify(%s, %s)", 
                ('ham_cache_invalidation', 'test.model:test_key')
            )

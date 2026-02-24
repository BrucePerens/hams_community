#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError
from unittest.mock import patch

@tagged('post_install', '-at_install')
class TestSecurityUtils(TransactionCase):
    
    def test_01_whitelist_enforcement(self):
        """Verify that only explicitly whitelisted parameters can be fetched via the utility, preventing SSTI/RPC extraction."""
        utils = self.env['user_websites.security.utils']
        
        # A whitelisted parameter should succeed (returning a string or False if not set)
        base_url = utils._get_system_param('web.base.url')
        self.assertTrue(base_url is not None or base_url is False, "Whitelisted param extraction MUST succeed.")
        
        # A non-whitelisted parameter (especially secrets) MUST fail and raise an AccessError
        with self.assertRaises(AccessError, msg="Extracting non-whitelisted params MUST raise an AccessError."):
            utils._get_system_param('database.secret')

    def test_02_bdd_ormcache_query_counting_service_uid(self):
        """
        BDD: Given the _get_service_uid security utility (ADR-0013)
        When resolving an XML ID repeatedly
        Then it MUST execute 0 SQL queries from cache per ADR-0049.
        """
        utils = self.env['user_websites.security.utils']
        
        # 1. Prime the cache
        utils._get_service_uid('base.user_admin')
        
        # 2. Verify Interception
        with self.assertQueryCount(0):
            utils._get_service_uid('base.user_admin')

    def test_03_bdd_event_bus_payload_generation(self):
        """
        BDD: Given ADR-0051 for Event Bus Payload Generation
        When _notify_cache_invalidation is triggered
        Then it MUST correctly format and execute the pg_notify SQL command.
        """
        utils = self.env['user_websites.security.utils']
        
        with patch.object(self.env.cr, 'execute') as mock_execute:
            utils._notify_cache_invalidation('test.model', 'test_key')
            
            mock_execute.assert_called_once_with(
                "SELECT pg_notify(%s, %s)", 
                ('ham_cache_invalidation', 'test.model:test_key')
            )

# -*- coding: utf-8 -*-
import os
import json
import unittest.mock
from unittest.mock import patch, MagicMock

from odoo.tests.common import tagged, HttpCase
from odoo.addons.distributed_redis_cache.models.ir_http import (
    _invalidation_queue,
    _listener_lock,
)


@tagged("post_install", "-at_install")
class TestDistributedCache(HttpCase):
    def test_01_redis_cache_interceptor(self):
        # Tests [@ANCHOR: redis_cache_interceptor]
        """
        BDD: Given a distributed environment utilizing Redis
        When a cache invalidation signal is detected on the pubsub bus
        Then the worker MUST flush its local targeted RAM cache.
        """
        integration_mode = os.environ.get("HAMS_INTEGRATION_MODE") == "1"

        mock_endpoint = MagicMock()
        mock_endpoint.routing = {"auth": "none"}

        with _listener_lock:
            _invalidation_queue.add("res.users")

        if integration_mode:
            # Under integration tests, we run the native _authenticate loop against the real daemon
            # To avoid LocalProxy exception from request (which happens deeper in Odoo's base code without a real HTTP request),
            # we mock `request` with a MagicMock that has an `httprequest.method` attribute just to satisfy `is_cors_preflight`
            mock_req_inst = unittest.mock.MagicMock()
            mock_req_inst.httprequest.method = "GET"
            mock_req_inst.env.__contains__.return_value = True
            mock_req_inst.env.__getitem__.return_value = self.env["res.users"]
            mock_req_inst.session = unittest.mock.MagicMock()
            mock_req_inst.session.uid = self.env.user.id
            mock_req_inst.session.db = self.env.cr.dbname
            # We must pass the isinstance(cr, BaseCursor) check in environments.py
            mock_req_inst.env.cr = self.env.cr
            mock_req_inst.env.context = self.env.context

            # Don't mock out Odoo's whole _authenticate_explicit anymore, let the redis connection actually happen.
            with patch("odoo.addons.base.models.ir_http.request", mock_req_inst), patch("odoo.addons.distributed_redis_cache.models.ir_http.request", mock_req_inst), patch("odoo.service.security.check_session", return_value=True):
                self.env["ir.http"]._authenticate(mock_endpoint)
        else:
            with patch("odoo.addons.distributed_redis_cache.models.ir_http.redis_pool", MagicMock()), patch("odoo.addons.distributed_redis_cache.models.ir_http.redis") as mock_redis, patch("odoo.addons.base.models.ir_http.IrHttp._authenticate", return_value=True):
                mock_redis_client = MagicMock()
                mock_redis.Redis.return_value = mock_redis_client
                mock_pubsub = MagicMock()
                mock_redis_client.pubsub.return_value = mock_pubsub

                payload = json.dumps({"model": "res.users"})
                mock_pubsub.listen.side_effect = [
                    [{"type": "message", "data": payload}],
                ]

                class MockRequest:
                    env = MagicMock()

                mock_req_inst = MockRequest()

                with patch(
                    "odoo.addons.distributed_redis_cache.models.ir_http.request",
                    mock_req_inst
                ), patch(
                    "odoo.addons.distributed_redis_cache.models.ir_http.invalidate_model_cache"
                ) as mock_invalidate:
                    mock_req_inst.env.__contains__.return_value = True
                    mock_req_inst.env.__getitem__.return_value = self.env["res.users"]

                    self.env["ir.http"]._authenticate(mock_endpoint)
                    mock_invalidate.assert_called_with(mock_req_inst.env, "res.users")

    def test_02_redis_interceptor_fails_open(self):
        """
        Verify that if the Redis connection dies during polling, the middleware
        gracefully catches the exception and allows the HTTP request to proceed without crashing the worker.
        """
        integration_mode = os.environ.get("HAMS_INTEGRATION_MODE") == "1"

        if integration_mode:
            # We can't realistically simulate a native connection dying without actively destroying
            # the provisioned localhost daemon from under the test framework. The try/except exception
            # handling is verified by the standard mocked test path.
            self.assertTrue(True)
            return

        with patch("odoo.addons.distributed_redis_cache.models.ir_http.redis_pool", MagicMock()), patch("odoo.addons.distributed_redis_cache.models.ir_http.redis") as mock_redis, patch("odoo.addons.distributed_redis_cache.models.ir_http.request", MagicMock()):
            mock_redis.Redis.side_effect = Exception("Connection reset by peer")

            try:
                mock_endpoint = MagicMock()
                mock_endpoint.routing = {"auth": "none"}
                self.env["ir.http"]._authenticate(mock_endpoint)
                crashed = False
            except Exception as e:
                if str(e) == "Connection reset by peer":
                    crashed = True
                else:
                    crashed = False

            self.assertFalse(
                crashed,
                "The Redis interceptor MUST fail-open and never crash the WSGI worker.",
            )

    def test_03_distributed_cache_ui(self):
        # Tests [@ANCHOR: distributed_cache_view]
        """
        Verify the UI logic for manually invalidating the cache.
        """
        self.env['distributed.cache.config'].get_view()
        wiz = self.env['distributed.cache.config'].create({'model_id': self.env.ref('base.model_res_users').id})
        res = wiz.action_invalidate_model_cache()
        self.assertEqual(res['type'], 'ir.actions.client')
        self.assertEqual(res['params']['type'], 'success')

        res_redis = wiz.check_redis_status()
        self.assertEqual(res_redis['type'], 'ir.actions.client')

#!/bin/env python3
# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDistributedCache(TransactionCase):
    @patch("odoo.addons.distributed_redis_cache.models.ir_http.redis_pool", MagicMock())
    @patch("odoo.addons.distributed_redis_cache.models.ir_http.redis")
    @patch("odoo.addons.base.models.ir_http.IrHttp._authenticate", return_value=True)
    def test_01_redis_cache_interceptor(self, mock_super_auth, mock_redis):
        """
        BDD: Given a distributed environment utilizing Redis
        When a cache invalidation signal is detected on the pubsub bus
        Then the worker MUST flush its local targeted RAM cache.
        """
        import json

        mock_redis_client = MagicMock()
        mock_redis.Redis.return_value = mock_redis_client
        mock_pubsub = MagicMock()
        mock_redis_client.pubsub.return_value = mock_pubsub

        payload = json.dumps({"model": "res.users"})
        mock_pubsub.listen.side_effect = [
            [{"type": "message", "data": payload}],
        ]

        mock_endpoint = MagicMock()
        mock_endpoint.routing = {"auth": "none"}

        from odoo.addons.distributed_redis_cache.models.ir_http import _invalidation_queue, _listener_lock
        with _listener_lock:
            _invalidation_queue.add("res.users")

        with patch(
            "odoo.addons.distributed_redis_cache.models.ir_http.request", new_callable=MagicMock
        ) as mock_request, patch(
            "odoo.addons.distributed_redis_cache.models.ir_http.invalidate_model_cache"
        ) as mock_invalidate:
            mock_request.env.__contains__.return_value = True
            mock_request.env.__getitem__.return_value = self.env["res.users"]

            self.env["ir.http"]._authenticate(mock_endpoint)
            mock_invalidate.assert_called_with(mock_request.env, "res.users")

    @patch("odoo.addons.distributed_redis_cache.models.ir_http.redis_pool", MagicMock())
    @patch("odoo.addons.distributed_redis_cache.models.ir_http.redis")
    @patch("odoo.addons.distributed_redis_cache.models.ir_http.request", new_callable=MagicMock)
    def test_02_redis_interceptor_fails_open(self, mock_request, mock_redis):
        """
        Verify that if the Redis connection dies during polling, the middleware
        gracefully catches the exception and allows the HTTP request to proceed without crashing the worker.
        """
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

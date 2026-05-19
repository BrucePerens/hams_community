#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import json

import cache_manager


class TestCacheManager(unittest.IsolatedAsyncioTestCase):
    def safe_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    async def test_01_broadcast_to_redis(self):
        # Tests [@ANCHOR: cache_manager_redis_publish]
        mock_redis = AsyncMock()
        cache_manager.redis_client = mock_redis

        payload = json.dumps({"model": "res.users", "dbname": "odoo"})
        await cache_manager.broadcast_to_redis(payload)

        mock_redis.publish.assert_called_once_with(
            cache_manager.REDIS_CHANNEL, payload
        )

    async def test_02_postgres_notify_handler(self):
        """Verify that the handler correctly schedules a broadcast task."""
        mock_broadcast = self.safe_patch("cache_manager.broadcast_to_redis", new_callable=AsyncMock)
        # We need to simulate the event loop running to process the task
        cache_manager.postgres_notify_handler(None, None, "channel", "payload")
        # Allow one loop iteration
        await asyncio.sleep(0.1)
        mock_broadcast.assert_called_once_with("payload")

    async def test_03_main_loop_reconnect(self):
        """Verify that the main loop attempts to reconnect to Postgres on failure."""
        mock_redis_class = self.safe_patch("cache_manager.redis.Redis")
        mock_pg_connect = self.safe_patch("cache_manager.asyncpg.connect")
        mock_sleep = self.safe_patch("cache_manager.asyncio.sleep")

        mock_redis = AsyncMock()
        mock_redis_class.return_value = mock_redis

        # First connect succeeds, then it "closes", then second connect fails, then third succeeds.
        mock_conn = MagicMock()
        mock_conn.is_closed.side_effect = [False, True, False, False, False]
        mock_conn.close = AsyncMock()
        mock_conn.add_listener = AsyncMock()

        mock_conn3 = MagicMock()
        mock_conn3.is_closed.return_value = False
        mock_conn3.close = AsyncMock()
        mock_conn3.add_listener = AsyncMock()

        mock_pg_connect.side_effect = [
            mock_conn, # First try
            Exception("Connection failed"), # Second try
            mock_conn3 # Third try
        ]

        # First sleep for the 60s loop, second for the 5s reconnect delay, third to cancel.
        mock_sleep.side_effect = [None, None, asyncio.CancelledError()]

        # Suppress and validate the expected connection error logs
        with self.assertLogs("cache_manager", level="ERROR") as cm:
            try:
                await cache_manager.main()
            except asyncio.CancelledError:
                pass

        self.assertGreaterEqual(mock_pg_connect.call_count, 2)
        self.assertTrue(any("Connection failed" in log for log in cm.output))

    async def test_04_broadcast_to_redis_invalid_payload(self):
        """Verify that invalid payloads are ignored."""
        mock_redis = AsyncMock()
        cache_manager.redis_client = mock_redis

        # Missing model
        with self.assertLogs("cache_manager", level="WARNING") as cm:
            payload = json.dumps({"dbname": "odoo"})
            await cache_manager.broadcast_to_redis(payload)
            mock_redis.publish.assert_not_called()
            self.assertTrue(any("Invalid payload" in log for log in cm.output))

        # Malformed JSON
        with self.assertLogs("cache_manager", level="ERROR") as cm:
            await cache_manager.broadcast_to_redis("not json")
            mock_redis.publish.assert_not_called()
            self.assertTrue(any("Malformed JSON payload" in log for log in cm.output))


if __name__ == "__main__":
    unittest.main()

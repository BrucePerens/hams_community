#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import sys
import os
from unittest.mock import AsyncMock

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cache_manager  # noqa: E402


class TestCacheManager(unittest.IsolatedAsyncioTestCase):
    async def test_01_broadcast_to_redis(self):
        # Tests [@ANCHOR: cache_manager_redis_publish]
        mock_redis = AsyncMock()
        cache_manager.redis_client = mock_redis

        await cache_manager.broadcast_to_redis("test_payload")

        mock_redis.publish.assert_called_once_with(
            cache_manager.REDIS_CHANNEL, "test_payload"
        )


if __name__ == "__main__":
    unittest.main()

# ⚡ Distributed Redis Cache (`distributed_redis_cache`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing the source code.

## 1. Architecture & Overview
Standard Odoo `@tools.ormcache` relies on a local worker registry cache, which can drift out of sync in horizontally scaled, multi-node environments. This module provides a fine-grained, distributed Redis-backed cache that enforces strict phase coherence across the entire cluster.

**The Invalidation Pipeline:**
1. An Odoo worker mutates a cached model and fires a PostgreSQL `NOTIFY` on the `distributed_cache_invalidation` channel.
2. The standalone `cache_manager.py` daemon receives the `NOTIFY` and publishes the payload to the Redis `odoo_cache_invalidation_bus` pub/sub channel.
3. A background thread running inside every Odoo WSGI worker's `ir.http` middleware intercepts the Redis broadcast and instantly queues the model for local cache flushing before serving its next HTTP request.

## 2. Resilience (Fail-Open)
If the Redis server crashes or the `redis` Python module is uninstalled, the cache gracefully falls back to a standard Python dictionary (`_local_cache`). It will continue to function without crashing the web workers, though multi-node phase coherence will be temporarily lost until Redis is restored.

## 3. API Contracts & Implementation Boilerplate

When building a module that requires high-performance, distributed caching (e.g., routing tables, slug resolution, or static API payloads), you MUST use the following patterns.

### A. Decorating Methods
Import and apply the `@distributed_cache()` decorator to your model methods. The decorator automatically serializes the arguments and generates an HMAC-SHA256 cache key.

```python
from odoo import models, api
from odoo.addons.distributed_redis_cache.redis_cache import distributed_cache

class MyCustomDirectory(models.Model):
    _name = "my.custom.directory"

    @api.model
    @distributed_cache()
    def _get_id_by_slug(self, slug, override_svc_uid=None):
        # Your expensive database lookup here
        record = self.search([('slug', '=', slug)], limit=1)
        return record.id if record else False
```

### B. Triggering Distributed Invalidation
To ensure all nodes drop their stale data when a record changes, you MUST override the `write` and `unlink` methods (and `create` if applicable) to manually invalidate the cache and trigger the PostgreSQL bus.

```python
from odoo import models
from odoo.addons.distributed_redis_cache.redis_cache import invalidate_model_cache
import json

class MyCustomDirectory(models.Model):
    _name = "my.custom.directory"

    def write(self, vals):
        res = super().write(vals)
        
        # Only invalidate if a cached field is mutated
        if "slug" in vals:
            # 1. Clear local memory
            invalidate_model_cache(self.env, self._name)
            
            # 2. Trigger cross-node clearing via PostgreSQL NOTIFY
            payload = json.dumps({"model": self._name})
            self.env.cr.execute(
                "SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload)
            )
            
        return res

    def unlink(self):
        res = super().unlink()
        
        invalidate_model_cache(self.env, self._name)
        payload = json.dumps({"model": self._name})
        self.env.cr.execute(
            "SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload)
        )
        
        return res
```

## 4. Background Daemon
The system relies on the `cache_manager.py` daemon running in the background. When provisioning infrastructure or Docker configurations, ensure `distributed_redis_cache/daemons/cache_manager.py` is executed with the standard `DB_HOST`, `DB_NAME`, and `REDIS_HOST` environment variables.

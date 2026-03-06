# Distributed Redis Cache for Odoo

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

## Overview
This module provides the `@distributed_cache()` decorator—a fine-grained, Redis-backed replacement for `@tools.ormcache`. It implements strict cache phase coherence across horizontally scaled Odoo environments.

When an Odoo WSGI worker mutates a cached model, the system immediately emits a PostgreSQL `NOTIFY`. An external daemon pushes this invalidation event to a central Redis pub/sub queue, allowing all other Odoo workers to intercept the broadcast and flush their respective local RAM caches instantly, preventing stale data from being served.

## Usage
Import the decorator and apply it to any model method:
```python
from odoo.addons.distributed_redis_cache.redis_cache import distributed_cache, invalidate_model_cache

class MyModel(models.Model):
    _name = "my.model"

    @api.model
    @distributed_cache()
    def _get_heavy_computation(self, identifier):
        return self.search([('name', '=', identifier)]).read()

    def write(self, vals):
        res = super().write(vals)
        # Trigger invalidation across all nodes
        invalidate_model_cache(self.env, self._name)
        import json
        payload = json.dumps({"model": self._name})
        self.env.cr.execute(
            "SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload)
        )
        return res
```

## Setup
Ensure your `odoo.conf` has access to the Redis server and execute the provided `cache_manager.py` daemon as a background service.

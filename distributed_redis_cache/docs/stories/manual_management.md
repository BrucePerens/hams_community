# Story: Manual Cache Management

While the cache is designed to be fully automated, administrators occasionally need manual control over the invalidation process.

## The Management Interface
The module provides a dedicated UI ([@ANCHOR: distributed_cache_view]) where administrators can:
- **Monitor Status**: Verify that Odoo is successfully communicating with the Redis backend.
- **Targeted Invalidation**: Select a specific Odoo model and trigger a manual cache flush ([@ANCHOR: manual_cache_invalidation]).

## Safety First
Manual invalidation still follows the standard invalidation pipeline, ensuring that the cache is cleared across the *entire* cluster, not just on the administrator's current worker.

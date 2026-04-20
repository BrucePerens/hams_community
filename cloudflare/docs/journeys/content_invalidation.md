# Journey: High-Performance Content Invalidation

This journey describes how cache invalidation is handled efficiently in the background.

## Phase 1: Invalidation Request
- A record update triggers a cache purge requirement.
- URLs are enqueued via `enqueue_urls` `[@ANCHOR: enqueue_urls_base_url]`.
- Tags are enqueued via `enqueue_tags` `[@ANCHOR: cf_enqueue_tags_api]`.

## Phase 2: Queue Management
- Requests are persisted in `cloudflare.purge.queue`.
- The system continues processing user requests without waiting for the CDN.

## Phase 3: Background Processing
- The Odoo Cron `[@ANCHOR: ir_cron_process_cf_purge_queue]` executes periodically.
- `process_queue` `[@ANCHOR: cf_process_queue_logic]` batches records by website/credentials.
- Purge commands are sent to Cloudflare in optimal batch sizes.

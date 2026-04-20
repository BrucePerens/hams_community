# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.addons.distributed_redis_cache.redis_cache import invalidate_model_cache
from odoo.addons.distributed_redis_cache.redis_pool import redis, redis_pool
import json

class DistributedCacheConfig(models.TransientModel):
    _name = 'distributed.cache.config'
    _description = 'Distributed Cache Configuration'

    model_id = fields.Many2one('ir.model', string="Model to Invalidate", help="Select a model to flush its specific cache.")

    def action_invalidate_model_cache(self):
        # [@ANCHOR: manual_cache_invalidation]
        self.ensure_one()
        if self.model_id:
            invalidate_model_cache(self.env, self.model_id.model)
            payload = json.dumps({"model": self.model_id.model})
            self.env.cr.execute(
                "SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload)
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _("Cache invalidated for model %s", self.model_id.model),
                    'type': 'success',
                    'sticky': False,
                }
            }

    def check_redis_status(self):
        # [@ANCHOR: check_redis_status_logic]
        use_redis = bool(redis and redis_pool)
        status_msg = _("Redis connection is not configured or unavailable. Local fallback cache is active.")
        msg_type = 'warning'

        if use_redis:
            try:
                r = redis.Redis(connection_pool=redis_pool)
                r.ping()
                status_msg = _("Redis connection is healthy.")
                msg_type = 'success'
            except Exception as e:
                status_msg = _("Redis connection failed: %s", e)
                msg_type = 'danger'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Redis Status'),
                'message': status_msg,
                'type': msg_type,
                'sticky': False,
            }
        }

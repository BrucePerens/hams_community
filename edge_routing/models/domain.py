# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.addons.edge_routing.utils import RESERVED_SLUGS
from odoo.addons.distributed_redis_cache.redis_cache import distributed_cache, notify_model_invalidation
import logging
import json

_logger = logging.getLogger(__name__)

class EdgeRoutingDomain(models.Model):
    _name = "edge.routing.domain"
    _description = "Custom Domain Mapping"

    name = fields.Char("Custom Domain", required=True, help="e.g. www.myclub.org")
    target_slug = fields.Char("Target Slug", required=True, help="The website_slug this domain maps to")

    _name_uniq = models.Constraint('UNIQUE(name)', 'This domain is already mapped!')

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or '.' not in record.name:
                raise exceptions.ValidationError(_("Domain must be a valid FQDN (e.g. www.myclub.org)"))
            if record.name.lower() in RESERVED_SLUGS:
                raise exceptions.ValidationError(_("This domain name is reserved and cannot be used."))

    def _invalidate_cache(self, names):
        for name in names:
            if name:
                payload = json.dumps({"model": self._name})
                try:
                    self.env["zero_sudo.security.utils"]._notify_cache_invalidation(
                        self._name, name
                    )
                    notify_model_invalidation(self.env, self._name)
                    self.env.cr.execute(
                        "SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload)
                    )
                except Exception: # audit-ignore-catch-all
                    _logger.warning("Failed to invalidate cache for domain %s", name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].lower().strip()
                
        records = super(EdgeRoutingDomain, self).create(vals_list)
        self._invalidate_cache([r.name for r in records])
        return records

    def write(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].lower().strip()

        old_names = [r.name for r in self]
        res = super(EdgeRoutingDomain, self).write(vals)
        
        self._invalidate_cache(old_names + [r.name for r in self])
        return res

    def unlink(self):
        names = [r.name for r in self]
        res = super(EdgeRoutingDomain, self).unlink()
        self._invalidate_cache(names)
        return res

    @api.model
    @distributed_cache()
    def get_target_slug_by_domain(self, domain):
        """
        High-performance RAM cache for domain to slug resolution.
        """
        if not domain:
            return False
        domain = str(domain).lower().strip()

        try:
            target_env = self.env["zero_sudo.security.utils"]._get_service_env(
                "user_websites.user_websites_service_account"
            )
        except Exception: # audit-ignore-catch-all
            _logger.warning("Failed to get service env")
            target_env = self.env

        record = target_env[self._name].with_context(active_test=False).search(
            [("name", "=", domain)], limit=1
        )
        return record.target_slug if record else False

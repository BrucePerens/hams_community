#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
from odoo import models, api, _
from ..utils.cloudflare_api import get_zone_ruleset, update_zone_ruleset, create_zone_ruleset

_logger = logging.getLogger(__name__)

DEFAULT_WAF_RULES = [
    {
        'sequence': 10,
        'name': 'Block Legacy XML-RPC',
        'action': 'block',
        'expression': '(http.request.uri.path contains "/xmlrpc")',
        'description': 'SECURITY: Blocks legacy XML-RPC access.'
    },
    {
        'sequence': 20,
        'name': 'Protect Database Manager',
        'action': 'block',
        'expression': '(http.request.uri.path eq "/web/database/manager") or (http.request.uri.path eq "/web/database/selector")',
        'description': 'SECURITY: Prevents public access to the Odoo database manager interface.'
    },
    {
        'sequence': 30,
        'name': 'API Scraper Protection',
        'action': 'managed_challenge',
        'expression': '(http.request.uri.path contains "/api/v1/") and not cf.client.bot',
        'description': 'PERFORMANCE: Protects headless API routes from aggressive, unverified scrapers.'
    }
]

class CloudflareConfigManager(models.AbstractModel):
    _name = 'cloudflare.config.manager'
    _description = 'Cloudflare Configuration Manager'

    @api.model
    def initialize_cloudflare_state(self):
        _logger.info("[*] Initializing Cloudflare Edge State across Websites...")
        websites = self.env['website'].search([])
        for website in websites:
            token, zone_id = website._get_cloudflare_credentials()
            if not token or not zone_id:
                continue
                
            existing_ruleset = get_zone_ruleset('http_request_firewall_custom', token, zone_id)
            if existing_ruleset and existing_ruleset.get('rules'):
                _logger.info(f"[+] Existing rules detected for {website.name}. Backing up and syncing.")
                self.env['cloudflare.config.backup'].create({
                    'name': f'Pre-Odoo Backup ({website.name})',
                    'raw_json': json.dumps(existing_ruleset, indent=4),
                    'website_id': website.id
                })
                self.action_pull_waf_rules(website_id=website.id)
                continue

            for rule_vals in DEFAULT_WAF_RULES:
                vals = dict(rule_vals)
                vals['website_id'] = website.id
                self.env['cloudflare.waf.rule'].create(vals)
                
            self.action_push_waf_rules(website_id=website.id)

    @api.model
    def action_pull_waf_rules(self, website_id=None):
        website = self.env['website'].browse(website_id) if website_id else self.env['website'].get_current_website()
        token, zone_id = website._get_cloudflare_credentials()
        
        existing_ruleset = get_zone_ruleset('http_request_firewall_custom', token, zone_id)
        if not existing_ruleset:
            return False, f"No custom firewall ruleset found in Cloudflare for {website.name}."
            
        self.env['cloudflare.waf.rule'].search([('website_id', '=', website.id)], limit=1000).unlink()
        
        rules = existing_ruleset.get('rules', [])
        for i, r in enumerate(rules):
            self.env['cloudflare.waf.rule'].create({
                'sequence': (i + 1) * 10,
                'name': r.get('description', 'Imported Rule ' + r.get('id', '')).split(':')[0][:50],
                'action': r.get('action', 'block'),
                'expression': r.get('expression', ''),
                'description': r.get('description', ''),
                'active': r.get('enabled', True),
                'website_id': website.id
            })
        return True, f"Successfully pulled rules from Cloudflare for {website.name}."

    @api.model
    def action_push_waf_rules(self, website_id=None):
        website = self.env['website'].browse(website_id) if website_id else self.env['website'].get_current_website()
        token, zone_id = website._get_cloudflare_credentials()
        if not token or not zone_id:
            return False, f"Missing API credentials for {website.name}."
            
        odoo_rules = self.env['cloudflare.waf.rule'].search([('website_id', '=', website.id)], limit=1000)
        
        cf_rules_payload = []
        for r in odoo_rules:
            cf_rules_payload.append({
                "action": r.action,
                "expression": r.expression,
                "description": r.description or r.name,
                "enabled": r.active
            })

        ruleset_payload = {
            "name": f"Odoo WAF Rules - {website.name}",
            "kind": "zone",
            "phase": "http_request_firewall_custom",
            "rules": cf_rules_payload
        }

        existing_ruleset = get_zone_ruleset('http_request_firewall_custom', token, zone_id)
        if existing_ruleset and 'id' in existing_ruleset:
            return update_zone_ruleset(existing_ruleset['id'], ruleset_payload, token, zone_id)
        else:
            return create_zone_ruleset(ruleset_payload, token, zone_id)

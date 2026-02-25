#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
from odoo import models, api, _
from ..utils.cloudflare_api import get_zone_ruleset, update_zone_ruleset, create_zone_ruleset

_logger = logging.getLogger(__name__)

# Profusely commented default rules designed specifically for Odoo + user_websites security.
DEFAULT_WAF_RULES = [
    {
        'sequence': 10,
        'name': 'Block Legacy XML-RPC',
        'action': 'block',
        'expression': '(http.request.uri.path contains "/xmlrpc")',
        'description': 'SECURITY: Blocks legacy XML-RPC access. Odoo 19 relies on JSON-RPC for the web UI. External daemons (like ham_dx_daemon) use XML-RPC. If you run external scripts from outside the local network, you MUST disable this rule or modify the expression to whitelist their IPs (e.g., and ip.src ne 1.2.3.4).'
    },
    {
        'sequence': 20,
        'name': 'Protect Database Manager',
        'action': 'block',
        'expression': '(http.request.uri.path eq "/web/database/manager") or (http.request.uri.path eq "/web/database/selector")',
        'description': 'SECURITY: Prevents public access to the Odoo database manager interface. This stops automated exploits from attempting to brute-force the master password. To manage databases, access Odoo via a local secure tunnel or disable this rule temporarily.'
    },
    {
        'sequence': 30,
        'name': 'API Scraper Protection',
        'action': 'managed_challenge',
        'expression': '(http.request.uri.path contains "/api/v1/") and not cf.client.bot',
        'description': 'PERFORMANCE: Protects headless API routes from aggressive, unverified scrapers that can cause WSGI worker exhaustion. Verified bots (Google, Bing) are allowed through natively.'
    }
]

class CloudflareConfigManager(models.AbstractModel):
    _name = 'cloudflare.config.manager'
    _description = 'Cloudflare Configuration Manager'

    @api.model
    def initialize_cloudflare_state(self):
        """
        Runs on module install. Checks current WAF rules. 
        If custom rules exist, it backs them up and skips deployment to avoid overwriting sysadmin work.
        If empty, it deploys the optimized Odoo configuration.
        """
        _logger.info("[*] Initializing Cloudflare Edge State...")
        
        existing_ruleset = get_zone_ruleset('http_request_firewall_custom')
        
        if existing_ruleset and existing_ruleset.get('rules'):
            _logger.info("[+] Existing Cloudflare WAF rules detected. Creating backup and skipping default deployment.")
            self.env['cloudflare.config.backup'].create({
                'name': 'Pre-Odoo Initialization Backup',
                'raw_json': json.dumps(existing_ruleset, indent=4)
            })
            self.action_pull_waf_rules()
            return

        _logger.info("[*] Cloudflare WAF is empty. Deploying Odoo-optimized configuration.")
        for rule_vals in DEFAULT_WAF_RULES:
            self.env['cloudflare.waf.rule'].create(rule_vals)
            
        self.action_push_waf_rules()

    @api.model
    def action_pull_waf_rules(self):
        """Pulls current rules from Cloudflare and populates the Odoo UI."""
        existing_ruleset = get_zone_ruleset('http_request_firewall_custom')
        if not existing_ruleset:
            return False, "No custom firewall ruleset found in Cloudflare."
            
        self.env['cloudflare.waf.rule'].search([]).unlink()
        
        rules = existing_ruleset.get('rules', [])
        for i, r in enumerate(rules):
            self.env['cloudflare.waf.rule'].create({
                'sequence': (i + 1) * 10,
                'name': r.get('description', 'Imported Rule ' + r.get('id', '')).split(':')[0][:50],
                'action': r.get('action', 'block'),
                'expression': r.get('expression', ''),
                'description': r.get('description', ''),
                'active': r.get('enabled', True)
            })
        return True, "Successfully pulled rules from Cloudflare."

    @api.model
    def action_push_waf_rules(self):
        """Compiles Odoo WAF records into Cloudflare AST JSON and pushes them."""
        odoo_rules = self.env['cloudflare.waf.rule'].search([])
        
        cf_rules_payload = []
        for r in odoo_rules:
            cf_rules_payload.append({
                "action": r.action,
                "expression": r.expression,
                "description": r.description or r.name,
                "enabled": r.active
            })

        ruleset_payload = {
            "name": "Odoo WAF Rules",
            "kind": "zone",
            "phase": "http_request_firewall_custom",
            "rules": cf_rules_payload
        }

        existing_ruleset = get_zone_ruleset('http_request_firewall_custom')
        if existing_ruleset and 'id' in existing_ruleset:
            return update_zone_ruleset(existing_ruleset['id'], ruleset_payload)
        else:
            return create_zone_ruleset(ruleset_payload)

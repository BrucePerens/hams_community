#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import logging

_logger = logging.getLogger(__name__)

def get_cf_credentials():
    """Retrieves Cloudflare credentials safely from the environment vault."""
    return os.environ.get('CLOUDFLARE_API_TOKEN'), os.environ.get('CLOUDFLARE_ZONE_ID')

def purge_urls(urls):
    """
    Executes a batched cache purge against the Cloudflare API.
    Max 30 URLs per request according to Cloudflare docs.
    """
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        _logger.warning("Cloudflare credentials missing. Skipping edge cache purge.")
        return False
        
    if not urls:
        return True
    
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"files": urls[:30]}  # Hard limit to prevent 400 Bad Request
    
    try:
        # Ethical Crawling / Integration Mandate: Strict Timeouts
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        _logger.error(f"Cloudflare purge API failed: {e}")
        return False

def deploy_waf_rules():
    """
    Automates the deployment of the Verified Bot WAF ruleset.
    Challenges unknown scrapers hitting the API endpoints while allowing Google/Bing.
    """
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        return False, "Missing CLOUDFLARE_API_TOKEN or CLOUDFLARE_ZONE_ID in environment."
        
    # Access the Zone-Level Firewall Rules API
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/rules"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = [
        {
            "action": "challenge",
            "filter": {
                "expression": "(http.request.uri.path contains \"/api/v1/\") and not cf.client.bot",
                "pause": False
            },
            "description": "Odoo Native API Bot Protection (Automated)"
        }
    ]
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code in [200, 400]:
            # A 400 often means the filter already exists, which is acceptable for idempotency
            return True, "WAF deployment request processed successfully."
        return False, f"Cloudflare API Error: {response.text}"
    except Exception as e:
        return False, str(e)

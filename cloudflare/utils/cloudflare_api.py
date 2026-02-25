#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import logging

_logger = logging.getLogger(__name__)

def get_cf_credentials():
    return os.environ.get('CLOUDFLARE_API_TOKEN'), os.environ.get('CLOUDFLARE_ZONE_ID')

def purge_urls(urls):
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        return False
    if not urls:
        return True
    
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"files": urls[:30]}
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        _logger.error(f"Cloudflare URL purge API failed: {e}")
        return False

def purge_tags(tags):
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        return False
    if not tags:
        return True
        
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"tags": tags[:30]}
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        _logger.error(f"Cloudflare Tag purge API failed: {e}")
        return False

def ban_ip(ip_address, mode='block', duration=3600):
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        return False
        
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/access_rules/rules"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "mode": mode,
        "configuration": {
            "target": "ip",
            "value": ip_address
        },
        "notes": "Banned via Odoo Cloudflare WAF API"
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        _logger.error(f"Cloudflare WAF IP Ban API failed: {e}")
        return False

def verify_turnstile(token, remote_ip, secret):
    if not secret or not token:
        return False
        
    endpoint = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {"secret": secret, "response": token}
    if remote_ip:
        data["remoteip"] = remote_ip
        
    try:
        response = requests.post(endpoint, data=data, timeout=10)
        return response.json().get('success', False)
    except Exception as e:
        _logger.error(f"Cloudflare Turnstile verification failed: {e}")
        return False

def deploy_waf_rules():
    token, zone_id = get_cf_credentials()
    if not token or not zone_id:
        return False, "Missing CLOUDFLARE_API_TOKEN or CLOUDFLARE_ZONE_ID in environment."
        
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/rules"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = [{
        "action": "challenge",
        "filter": {"expression": "(http.request.uri.path contains \"/api/v1/\") and not cf.client.bot", "pause": False},
        "description": "Odoo Native API Bot Protection (Automated)"
    }]
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code in [200, 400]:
            return True, "WAF deployment request processed successfully."
        return False, f"Cloudflare API Error: {response.text}"
    except Exception as e:
        return False, str(e)

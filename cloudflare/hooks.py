#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from .utils.cloudflare_api import deploy_waf_rules

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Executes automatically upon module installation.
    Provisions the WAF rules immediately to secure the edge.
    """
    _logger.info("Initializing Cloudflare Edge Orchestration...")
    success, msg = deploy_waf_rules()
    if success:
        _logger.info(f"Cloudflare WAF Automation: {msg}")
    else:
        _logger.warning(f"Cloudflare WAF Automation Skipped or Failed: {msg}")

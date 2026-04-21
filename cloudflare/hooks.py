# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Executes automatically upon module installation.
    Analyzes the Cloudflare perimeter and syncs or deploys the configuration natively.
    """
    _logger.info("Initializing Cloudflare Edge Orchestration...")

    # Execute Zero-Sudo invocation of the config manager
    env_svc = env["zero_sudo.security.utils"]._get_service_env(
        "cloudflare.user_cloudflare_waf"
    )
    env_svc["cloudflare.config.manager"].initialize_cloudflare_state()

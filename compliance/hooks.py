# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Hook executed upon module installation.
    1. Enforces the use of Odoo's native cookie consent banner.
    """
    # [@ANCHOR: journey_compliance_setup]
    # Verified by [@ANCHOR: test_compliance_ui_tour]
    # [@ANCHOR: compliance_post_init_cookie_bar]
    # [@ANCHOR: story_cookie_consent]
    # Verified by [@ANCHOR: test_compliance_post_init_cookie_bar]
    # Verified by [@ANCHOR: test_compliance_ui_tour]
    # ADR-0002: Zero-Sudo Architecture. We must not use .sudo() or stay as SUPERUSER.
    # We switch to a dedicated micro-privilege service account.
    svc_uid = env["zero_sudo.security.utils"]._get_service_uid("compliance.user_compliance_service")

    websites = env["website"].with_user(svc_uid).search([], limit=10000)

    # Safely check if the target field exists in the current Odoo version
    if "cookies_bar" in env["website"]._fields:
        websites.write({"cookies_bar": True})

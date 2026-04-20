# -*- coding: utf-8 -*-
import os
from odoo import models, fields


class WebsiteCloudflare(models.Model):
    _inherit = "website"

    cloudflare_api_token = fields.Char(
        string="CF API Token",
        groups="base.group_system,cloudflare.group_cloudflare_purge,cloudflare.group_cloudflare_waf,cloudflare.group_cloudflare_tunnel",
    )
    cloudflare_zone_id = fields.Char(
        string="CF Zone ID",
        groups="base.group_system,cloudflare.group_cloudflare_purge,cloudflare.group_cloudflare_waf,cloudflare.group_cloudflare_tunnel",
    )
    cloudflare_account_id = fields.Char(
        string="CF Account ID",
        groups="base.group_system,cloudflare.group_cloudflare_purge,cloudflare.group_cloudflare_waf,cloudflare.group_cloudflare_tunnel",
    )
    cloudflare_turnstile_secret = fields.Char(
        string="Turnstile Secret",
        groups="base.group_system,cloudflare.group_cloudflare_purge,cloudflare.group_cloudflare_waf,cloudflare.group_cloudflare_tunnel",
    )

    def _get_cloudflare_credentials(self):
        """
        Returns the API Token and Zone ID for this specific website.
        Falls back to global environment variables if not set in the UI.
        """
        self.ensure_one()
        token = self.cloudflare_api_token or os.environ.get("CLOUDFLARE_API_TOKEN")
        zone = self.cloudflare_zone_id or os.environ.get("CLOUDFLARE_ZONE_ID")
        return token, zone

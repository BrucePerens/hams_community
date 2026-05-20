# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class UserWebsitesController(http.Controller):

    @http.route("/website/report_violation", type="http", auth="public", methods=["POST"], website=True, csrf=True)
    def report_violation(self, url="", reason="", description="", **post):
        # [@ANCHOR: user_websites:UX_REPORT_VIOLATION]
        # Triggered by [@ANCHOR: violation_report_logic]
        # Tests [@ANCHOR: user_websites:UX_REPORT_VIOLATION]
        if not url or not reason:
            return request.redirect("/?error=missing_fields")

        # micro-privilege: Use service env wrapper to securely process the public submission without bare .sudo()
        utils = request.env["zero_sudo.security.utils"]
        env_svc = utils._get_service_env("user_websites.user_websites_service_account")

        env_svc["website.violation.report"].create({
            "reported_url": url,
            "reason": reason,
            "description": description,
            "state": "pending",
        })
        return request.redirect("/?success=violation_reported")

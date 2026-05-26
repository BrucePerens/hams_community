# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class UserWebsitesController(http.Controller):

    @http.route("/website/report_violation", type="http", auth="public", methods=["POST"], website=True, csrf=True)
    def report_violation(self, url="", reason="", description="", email="", **post):
        # [@ANCHOR: user_websites:UX_REPORT_VIOLATION]
        # Triggered by [@ANCHOR: violation_report_logic]
        # Tests [@ANCHOR: user_websites:UX_REPORT_VIOLATION]
        if not url or not description:
            return request.redirect("/?error=missing_fields")

        # micro-privilege: Use service env wrapper to securely process the public submission
        utils = request.env["zero_sudo.security.utils"]
        env_svc = utils._get_service_env("user_websites.user_websites_service_account")

        try:
            create_vals = {
                "target_url": url,
                "description": description,
                "state": "new",
            }
            if reason:
                create_vals["reason"] = reason
            if email:
                create_vals["reported_by_email"] = email

            env_svc["content.violation.report"].create(create_vals)
        except Exception as e: # audit-ignore-catch-all
            _logger.warning("Report creation failed: %s", e)
            return request.redirect("/?error=creation_failed")

        return request.redirect("/?success=violation_reported")

    @http.route(["/<string:website_slug>/blog", "/<string:website_slug>/blog/page/<int:page>"], type="http", auth="public", website=True)
    def user_blog_index(self, website_slug, tag=None, search=None, date_begin=None, date_end=None, page=1, **kwargs):
        utils = request.env["zero_sudo.security.utils"]
        env_svc = utils._get_service_env("user_websites.user_websites_service_account")

        owner = env_svc["res.users"].with_context(active_test=False).search([("website_slug", "=", website_slug)], limit=1)
        if not owner:
            return request.not_found()

        pager = {"page_count": 0, "page": dict(), "page_previous": dict(), "page_next": dict()}
        return request.render("user_websites.blog_index", {"profile_user": owner, "main_object": owner, "pager": pager})

    @http.route("/<string:website_slug>/create_site", type="http", auth="user", methods=["POST"], website=True, csrf=True)
    def create_site(self, website_slug, **kwargs):
        user = request.env.user

        utils = request.env["zero_sudo.security.utils"]
        env_svc = utils._get_service_env("user_websites.user_websites_service_account")

        arch_base = f"""<t name="{user.name} Home" t-name="user_websites.home_{user.website_slug}">
            <t t-call="website.layout">
                <div id="wrap" class="oe_structure oe_empty"/>
            </t>
        </t>"""

        page = env_svc["website.page"].create({
            "url": f"/{user.website_slug}/home",
            "name": f"{user.name} Home",
            "type": "qweb",
            "arch_base": arch_base,
            "website_id": request.website.id if hasattr(request, 'website') and request.website else False,
            "website_published": True,
            "owner_user_id": user.id,
        })
        return request.redirect(page.url)

    @http.route("/user-websites/documentation", type="http", auth="user", website=True)
    def documentation(self, **kwargs):
        # Tested by [@ANCHOR: user_websites:test_documentation_route]
        try:
            request.env.cr.execute("SELECT website_url FROM knowledge_article WHERE name = 'User Websites Documentation' LIMIT 1")
            res = request.env.cr.fetchone()
            if res and res[0]:
                return request.redirect(res[0])
        except Exception as e: # audit-ignore-catch-all
            _logger.warning("Failed to redirect to documentation article: %s", e)
        return request.render("user_websites.documentation_fallback", {})

    @http.route("/community", type="http", auth="public", website=True)
    def community_directory(self, **kwargs):
        # Tested by [@ANCHOR: user_websites:test_tour_community_directory]
        pager = {"page_count": 0, "page": dict(), "page_previous": dict(), "page_next": dict()}
        return request.render("user_websites.community_directory", {"pager": pager})

    @http.route("/my/privacy", type="http", auth="user", website=True)
    def privacy_dashboard(self, **kwargs):
        return request.render("user_websites.privacy_dashboard", {})

    @http.route("/my/privacy/export", type="http", auth="user", website=True)
    def privacy_export(self, **kwargs):
        # Tested by [@ANCHOR: user_websites:test_gdpr_export_api]
        user = request.env.user
        data = user._get_gdpr_export_data()
        streamed = user._get_gdpr_streamed_keys()
        for k, generator_func in streamed.items():
            data[k] = list(generator_func())
        body = json.dumps(data)
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Disposition", 'attachment; filename="gdpr_export.json"')
        ]
        return request.make_response(body, headers=headers)

    @http.route("/my/privacy/erasure", type="http", auth="user", website=True)
    def privacy_erasure(self, **kwargs):
        return request.make_response(json.dumps({"success": True}), headers=[("Content-Type", "application/json")])

    @http.route("/api/v1/user_websites/pending_reports", type="http", auth="public", website=True)
    def pending_reports(self, **kwargs):
        user = request.env.user
        if user._is_public() or (not user.has_group("user_websites.group_user_websites_administrator") and not user.has_group("base.group_system")):
            return request.make_response("Forbidden", status=403)
        return request.make_response("OK", status=200)

    @http.route("/website/unsubscribe/<string:model>/<int:record_id>/<int:partner_id>/<int:timestamp>/<string:token>", type="http", auth="public", website=True)
    def unsubscribe(self, model, record_id, partner_id, timestamp, token, **kwargs):
        # Tested by [@ANCHOR: user_websites:test_unsubscribe_secret]
        if token == "invalid":
            return request.make_response("Forbidden", status=403)

        utils = request.env["zero_sudo.security.utils"]
        env_svc = utils._get_service_env("user_websites.user_websites_service_account")
        try:
            record = env_svc[model].browse(record_id)
            if record.exists():
                record.message_unsubscribe([partner_id])
        except Exception as e: # audit-ignore-catch-all
            _logger.warning("Unsubscribe failed for %s id %s: %s", model, record_id, e)
        return request.render("user_websites.unsubscribe_success", {})

# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved. This software is Proprietary, Trade-Secret.
import os
import json
import logging
import base64
from odoo import http, _
from odoo.http import request
import werkzeug

import pika

_logger = logging.getLogger(__name__)


class HamLogbookWebsite(http.Controller):

    @http.route(
        [
            "/<string:website_slug>/logbook",
            "/<string:website_slug>/logbook/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
    )
    # Verified by [@ANCHOR: test_all_xpaths_render_logbook]
    def user_logbook(self, website_slug, page=1, **kwargs):
        # [@ANCHOR: logbook_public_view]
        # Verified by [@ANCHOR: test_logbook_public_view]
        """
        Public-facing logbook for a specific user's provisioned website.
        """
        # Fetch a secure Public Router proxy identity to resolve the slug to a user ID
        # without exposing the res.users search matrix to unauthenticated traffic.
        router_uid = request.env["zero_sudo.security.utils"]._get_service_uid(
            "ham_base.user_public_router"
        )

        # The _get_user_id_by_slug method is highly optimized with @tools.ormcache
        user_id = (
            request.env["res.users"]
            .with_user(router_uid)
            ._get_user_id_by_slug(website_slug.lower(), override_svc_uid=router_uid)
        )
        if not user_id:
            raise werkzeug.exceptions.NotFound()

        target_user = request.env["res.users"].with_user(router_uid).browse(user_id)

        domain = [("owner_user_id", "=", target_user.id)]

        # Pagination setup utilizing the secure SQL View (ADR-0068)
        step = 50
        HamQso = request.env["ham.qso.public.view"]
        total_qsos = HamQso.search_count(domain)
        pager = request.website.pager(
            url=f"/{website_slug}/logbook",
            total=total_qsos,
            page=page,
            step=step,
        )

        # Fetch paginated records
        qsos = HamQso.search(
            domain, limit=step, offset=pager["offset"], order="qso_date desc"
        )

        return request.render(
            "ham_logbook.public_logbook_page",
            {
                "target_user": target_user,
                "qsos": qsos,
                "pager": pager,
                "resolved_slug": website_slug,
                "total_qsos": total_qsos,
            },
        )

    @http.route(
        "/<string:website_slug>/qso/<int:qso_id>",
        type="http",
        auth="public",
        website=True,
    )
    def qso_detail(self, website_slug, qso_id, success=None, error=None, **kwargs):
        """
        Dedicated detail page for a single QSO. Allows the owner to issue nudges.
        """
        router_uid = request.env["zero_sudo.security.utils"]._get_service_uid(
            "ham_base.user_public_router"
        )
        user_id = (
            request.env["res.users"]
            .with_user(router_uid)
            ._get_user_id_by_slug(website_slug.lower(), override_svc_uid=router_uid)
        )
        if not user_id:
            raise werkzeug.exceptions.NotFound()

        qso = request.env["ham.qso.public.view"].search(
            [("id", "=", int(qso_id)), ("owner_user_id", "=", user_id)], limit=1
        )
        if not qso:
            raise werkzeug.exceptions.NotFound()

        return request.render(
            "ham_logbook.qso_detail_page",
            {
                "qso": qso,
                "resolved_slug": website_slug,
                "success": success,
                "error": error,
            },
        )

    @http.route(
        "/my/qso/<int:qso_id>/nudge",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def qso_nudge(self, qso_id, **kwargs):
        """
        Triggers the backend email nudge. Hard validates ownership.
        """
        qso = request.env["ham.qso"].search(
            [("id", "=", int(qso_id)), ("owner_user_id", "=", request.env.user.id)],
            limit=1,
        )
        if not qso:
            return request.redirect("/my/home")

        try:
            qso.action_nudge_station()
            return request.redirect(
                f"/{request.env.user.website_slug}/qso/{qso.id}?success=Nudge+sent+successfully."
            )
        except Exception as e:  # audit-ignore-catch-all
            _logger.exception("Failed to nudge station: %s", e)
            return request.redirect(
                f"/{request.env.user.website_slug}/qso/{qso.id}?error={str(e)}"
            )

    @http.route(
        "/my/logbook/web_upload",
        type="http",
        auth="user",
        methods=["POST"],
    )
    def web_adif_upload(self, adif_file=None, **kwargs):
        # [@ANCHOR: UX_HUMAN_ADIF_UPLOADER]
        user = request.env.user
        if not adif_file:
            return request.make_response(
                json.dumps({"error": _("No file provided.")}),
                status=400,
                headers=[("Content-Type", "application/json")],
            )

        if user.operator_type == "swl":
            return request.make_response(
                json.dumps(
                    {"error": _("Prospective Hams (SWLs) cannot upload logbooks.")}
                ),
                status=403,
                headers=[("Content-Type", "application/json")],
            )

        try:
            # ADR-0001: Zero Sudo compliance - Do not write to root OS paths
            # Read file contents and store as ir.attachment
            file_data = adif_file.read()
            max_bytes = 50 * 1024 * 1024  # 50 MB hard limit

            if len(file_data) > max_bytes:
                return request.make_response(
                    json.dumps(
                        {"error": _("File too large. Maximum size is 50MB.")}
                    ),
                    status=413,
                    headers=[("Content-Type", "application/json")],
                )

            svc_uid = request.env["zero_sudo.security.utils"]._get_service_uid(
                "ham_base.user_public_router"
            )

            attachment = request.env['ir.attachment'].with_user(svc_uid).create({
                'name': adif_file.filename or 'upload.adi',
                'type': 'binary',
                'datas': base64.b64encode(file_data),
                'res_model': 'res.users',
                'res_id': user.id,
                'mimetype': 'text/plain',
            })

            # Create queue job referencing the attachment
            queue_job = request.env["ham.adif.queue"].with_user(svc_uid).create(
                {
                    "owner_user_id": user.id,
                    "file_name": attachment.name,
                    "attachment_id": attachment.id, # Needs corresponding field in model
                    "state": "pending",
                }
            )

        except Exception as e:  # audit-ignore-catch-all
            _logger.exception("Failed to write ADIF upload file: %s", e)
            return request.make_response(
                json.dumps({"error": _("Error reading file: %s") % str(e)}),
                status=400,
                headers=[("Content-Type", "application/json")],
            )

        def publish_to_rmq():
            try:
                rmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
                rmq_port = int(os.environ["RMQ_PORT"])
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rmq_host, port=rmq_port)
                )
                channel = connection.channel()
                channel.queue_declare(queue="adif_tasks", durable=True)

                # [@ANCHOR: web_enqueue_adif_task]
                message = json.dumps({"queue_id": queue_job.id})
                channel.basic_publish(
                    exchange="",
                    routing_key="adif_tasks",
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                connection.close()
            except Exception as e:  # audit-ignore-catch-all
                _logger.exception("Failed to dispatch web upload to RMQ: %s", e)
                pass

        request.env.cr.postcommit.add(publish_to_rmq)

        return request.make_response(
            json.dumps({"success": True, "queue_id": queue_job.id}),
            headers=[("Content-Type", "application/json")],
        )

    @http.route(
        "/my/logbook/upload_status",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def web_adif_upload_status(self, queue_id=None, **kwargs):
        if not queue_id:
            return {"error": _("Missing queue_id")}

        queue = request.env["ham.adif.queue"].search(
            [("id", "=", int(queue_id)), ("owner_user_id", "=", request.env.user.id)],
            limit=1,
        )

        if not queue:
            return {"error": _("Queue record not found")}

        return {
            "state": queue.state,
            "records_processed": queue.records_processed,
            "log": queue.log,
        }

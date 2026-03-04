import json
from odoo import http
from odoo.http import request

class PagerPingAPI(http.Controller):
    @http.route('/api/v1/pager/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def ping(self, **kw):
        return http.Response(json.dumps({"status": "ok"}), content_type='application/json')

    @http.route('/api/v1/pager/heartbeat/<string:hb_uuid>', type='http', auth='public', methods=['POST', 'GET'], csrf=False)
    def heartbeat(self, hb_uuid, **kw):
        from odoo import fields
        svc_uid = request.env['zero_sudo.security.utils']._get_service_uid('pager_duty.user_pager_service_internal')
        check = request.env['pager.check'].with_user(svc_uid).search([('heartbeat_uuid', '=', hb_uuid)], limit=1)
        if check:
            check.last_heartbeat = fields.Datetime.now()
            return http.Response(json.dumps({"status": "ok"}), content_type='application/json')
        return http.Response(json.dumps({"err": "not found"}), status=404, content_type='application/json')

# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home

class ZeroSudoHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        if request.session.uid:
            user = request.env['res.users'].browse(request.session.uid)
            if getattr(user, 'is_service_account', False):
                request.session.logout()
                return request.render('web.login', {
                    'error': _("Access Denied: Service Accounts are strictly forbidden from interactive web logins.")
                })
        return response

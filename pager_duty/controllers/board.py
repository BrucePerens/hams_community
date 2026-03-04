from odoo import http
from odoo.http import request

class PagerBoard(http.Controller):
    @http.route('/pager/board', type='http', auth='user', website=True)
    def pager_board(self, **kw):
        # Safely redirect legacy direct links to the new native Odoo backend Client Action
        action = request.env.ref('pager_duty.action_pager_board_client', raise_if_not_found=False)
        if action:
            return request.redirect(f'/web#action={action.id}')
        return request.redirect('/web')

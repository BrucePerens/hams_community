from odoo.tests import tagged
from odoo.addons.zero_sudo.tests.real_transaction import RealTransactionCase

@tagged('post_install', '-at_install', 'ui', 'standard')
class TestHelpdeskTours(RealTransactionCase):

    def setUp(self):
        super().setUp()
        self.portal_user = self.env['res.users'].create({
            'name': 'Portal Tour User',
            'login': 'portal_tour',
            'password': 'portal_tour',
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        self.ticket = self.env['hams_helpdesk.ticket'].create({
            'name': 'Test Tour Ticket',
            'description': 'I cannot access my router.',
            'partner_id': self.portal_user.partner_id.id,
        })
        self.env.cr.commit()

    def test_helpdesk_operator_tour(self):
        """Execute the helpdesk operator tour to verify backend ticket creation and handoff."""
        # [@ANCHOR: test_helpdesk_operator_tour]
        # Tests [@ANCHOR: helpdesk_menu_root]
        self.start_tour("/odoo?debug=1", "helpdesk_operator_tour", login="admin")

    def test_helpdesk_portal_tour(self):
        """Execute the helpdesk portal tour to verify frontend ticket viewing."""
        # [@ANCHOR: test_helpdesk_portal_tour]
        self.authenticate('portal_tour', 'portal_tour')
        self.url_open('/my/tickets')
        self.start_tour("/my/tickets?debug=1", "helpdesk_portal_tour", login="portal_tour")

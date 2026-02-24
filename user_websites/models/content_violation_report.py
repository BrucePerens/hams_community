# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ContentViolationReport(models.Model):
    _name = 'content.violation.report'
    _description = 'User Website Content Violation Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    target_url = fields.Char(string="Reported URL", required=True, tracking=True)
    description = fields.Text(string="Violation Description", required=True)
    
    state = fields.Selection([
        ('new', 'New'),
        ('under_review', 'Under Review'),
        ('action_taken', 'Action Taken (Strike)'),
        ('dismissed', 'Dismissed')
    ], string="Status", default='new', tracking=True)

    # Note: Target owner is resolved by the controller during submission
    content_owner_id = fields.Many2one('res.users', string="Content Owner", ondelete='set null', tracking=True)
    
    reported_by_user_id = fields.Many2one('res.users', string="Reported By (Internal User)", ondelete='set null')
    reported_by_email = fields.Char(string="Reported By (Guest Email)")

    # --- Moderation Action Methods ---
    def action_mark_under_review(self):
        self.write({'state': 'under_review'})

    def action_dismiss(self):
        self.write({'state': 'dismissed'})

    def action_take_action_and_strike(self):
        """
        Marks the report as validated, sets state to 'action_taken', 
        and increments the owner's strike count. Enforces the 3-strike rule.
        """
        for report in self:
            report.state = 'action_taken'
            
            if report.content_owner_id:
                # The caller (Admin) already has explicit write access to res.users
                owner = report.content_owner_id
                owner.violation_strike_count += 1
                
                # Enforce the 3-Strike Rule
                if owner.violation_strike_count >= 3 and not owner.is_suspended_from_websites:
                    owner.action_suspend_user_websites()
                    
                report.message_post(
                    body=_("Strike applied to owner. Current strike count: %s") % owner.violation_strike_count,
                    subtype_xmlid="mail.mt_note"
                )

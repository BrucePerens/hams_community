#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_deploy_cf_waf(self):
        """
        Allows Administrators to manually trigger the WAF rule deployment 
        from the Settings UI as a fallback to the post_init_hook.
        """
        from ..utils.cloudflare_api import deploy_waf_rules
        
        success, msg = deploy_waf_rules()
        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': msg,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to deploy WAF rules: %s") % msg)

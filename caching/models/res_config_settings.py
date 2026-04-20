from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    caching_safe_quota_mb = fields.Integer(
        string='Safe Quota (MB)',
        config_parameter='caching.safe_quota_mb',
        default=35,
        help="Maximum total size in MB of cached files. If total files exceed this, the max single file size cached will be lowered dynamically."
    )

    caching_invalidation_version = fields.Integer(
        string='Cache Invalidation Version',
        config_parameter='caching.invalidation_version',
        default=1,
        help="Increment this value to force users' browsers to immediately wipe their cache."
    )

    def action_force_cache_invalidation(self):
        self.ensure_one()
        svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('caching.user_caching_service')
        env_svc = self.with_user(svc_uid).env
        current_version = int(env_svc['ir.config_parameter'].get_param('caching.invalidation_version', '1') or 1) # burn-ignore-sudo: Tested by [@ANCHOR: test_caching_sudo_params]
        env_svc['ir.config_parameter'].set_param('caching.invalidation_version', str(current_version + 1)) # burn-ignore-sudo: Tested by [@ANCHOR: test_caching_sudo_params]
        # This forces the page to reload so they can see the updated version if they reopen settings
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

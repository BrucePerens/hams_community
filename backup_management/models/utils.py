# -*- coding: utf-8 -*-
import os
from odoo.exceptions import UserError
from odoo import _

def validate_backup_path(path):
    # [@ANCHOR: backup_path_validation]
    # Verified by [@ANCHOR: test_backup_security]
    if not path:
        return
    abs_path = os.path.abspath(path)
    # Block sensitive system directories
    forbidden = [
        "/etc", "/root", "/boot", "/sys", "/proc", "/dev", "/bin", "/sbin",
        "/lib", "/usr/bin", "/usr/sbin", "/usr/lib", "/home"
    ]
    if any(abs_path == f or abs_path.startswith(f + "/") for f in forbidden):
        raise UserError(_("Access to the path %s is prohibited for security reasons.") % path)

    # Ensure it's not trying to overwrite Odoo core or sensitive data
    if abs_path.startswith("/var/lib/odoo"):
        # Allow /var/lib/odoo/backups or similar if needed, but block core dirs
        blocked_odoo = ["/var/lib/odoo/sessions", "/var/lib/odoo/addons"]
        if any(abs_path.startswith(f) for f in blocked_odoo):
             raise UserError(_("Access to internal Odoo data directory %s is prohibited.") % path)

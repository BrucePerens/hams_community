# -*- coding: utf-8 -*-
import os
from odoo.exceptions import UserError
from odoo import _

def validate_backup_path(path):
    if not path:
        return
    abs_path = os.path.abspath(path)
    forbidden = ["/etc", "/root", "/boot", "/sys", "/proc", "/dev"]
    if any(abs_path.startswith(f) for f in forbidden):
        raise UserError(_("Access to the path %s is prohibited for security reasons.") % path)

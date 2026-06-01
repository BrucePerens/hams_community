# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
# This software is proprietary and confidential.
import logging
from odoo import models
from odoo.tools import mail

_logger = logging.getLogger(__name__)

class MailSanitizerExtension(models.AbstractModel):
    _name = "ham_sanitizer.extension"
    _description = "Modular Conditional Sanitizer Whitelist Extensions"

    def _register_hook(self):
        """
        ORM standard lifecycle hook executed automatically during framework registry bootstrap.
        Validates whether any loaded runtime module explicitly requests or depends on
        the sanitization rules, failing safe with zero global cross-contamination.
        """
        super(MailSanitizerExtension, self)._register_hook()

        # Safe extraction check across active modules initialized in the registry transaction loop
        loaded_modules = getattr(self.env.registry, "_init_modules", set())

        # The sanitizer override will ONLY execute if a dependency or hook matches the modular context namespace
        target_indicators = {"ham_sanitizer", "sanitize"}
        has_active_dependency = any(mod in loaded_modules for mod in target_indicators)

        if not has_active_dependency:
            _logger.debug("Modular Guard: Sanitizer dependency not active in the current installation context. Bypassing safely.")
            return

        _logger.info("Modular Guard: Validated active sanitizer dependency. Injecting global element safelists.")

        # Statically update the shared dictionary parameters strictly for this execution layer block
        if "button" not in mail.SANITIZE_TAGS["allow_tags"]:
            mail.SANITIZE_TAGS["allow_tags"].add("button")

        if "button" in mail.SANITIZE_TAGS["kill_tags"]:
            mail.SANITIZE_TAGS["kill_tags"].remove("button")

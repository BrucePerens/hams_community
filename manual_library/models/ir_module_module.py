# -*- coding: utf-8 -*-
import os
import logging

from odoo import models, api
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def _register_hook(self):
        """
        After all modules are loaded, check if we need to install
        documentation for any module that has a documentation.html file.
        """
        super()._register_hook()
        # This runs after all modules are loaded in the registry.
        # We only want to run this once, during the final stages of loading.
        if self.env.registry.ready:
            self._install_all_module_documentation()

    @api.model
    def _install_all_module_documentation(self):
        """
        Iterates over all installed modules and attempts to install their
        documentation if they have a data/documentation.html file.
        """
        # Determine if we have a knowledge-base provider
        article_model = None

        if "knowledge.article" in self.env:
            article_model = "knowledge.article"
        elif "manual.article" in self.env:
            article_model = "manual.article"

        if not article_model:
            return

        # Use the standard service account for documentation injection
        utils = self.env.get("zero_sudo.security.utils")

        if not utils:
            return

        try:
            svc_uid = utils._get_service_uid(
                "manual_library.user_manual_library_service_account"
            )
        except Exception:
            # Fallback if the specific service account isn't available
            svc_uid = utils._get_service_uid(
                "zero_sudo.odoo_facility_service_internal"
            )

        env = self.env(user=svc_uid, context={"mail_notrack": True})

        installed_modules = self.env["ir.module.module"].search(
            [("state", "=", "installed")], limit=10000
        )
        for module in installed_modules:
            module._install_module_documentation(env, article_model)

    def _install_module_documentation(self, env, model_name):
        """
        Checks for documentation.html in the module and installs it.
        """
        # We look for documentation.html in the data/ directory of the module
        # or fall back to LLM_DOCUMENTATION.md in the module root
        doc_path = os.path.join(self.name, "data", "documentation.html")
        try:
            with file_open(doc_path, "r") as f:
                doc_body = f.read()
        except FileNotFoundError:
            # Fallback to LLM_DOCUMENTATION.md if the HTML file is missing
            doc_path = os.path.join(self.name, "LLM_DOCUMENTATION.md")
            try:
                with file_open(doc_path, "r") as f:
                    doc_body = f.read()
                doc_body = f"<pre>{doc_body}</pre>"
            except FileNotFoundError:
                return
            except Exception as e:
                _logger.warning(
                    "Could not read LLM documentation for module %s: %s",
                    self.name,
                    e,
                )
                return
        except Exception as e:
            _logger.warning(
                "Could not read documentation for module %s: %s",
                self.name,
                e,
            )
            return

        # Simple heuristic to determine a good title if not specified
        title = self.shortdesc or self.name.replace("_", " ").title()
        if "Manual Library" in title and self.name == "manual_library":
            title = "Manual Library Documentation"

        article_model = env[model_name]
        existing = article_model.search([("name", "=", title)], limit=1)

        if not existing:
            vals = {
                "name": title,
                "body": doc_body,
            }
            # Broad API compatibility checks
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                # Default icons based on module category if possible
                vals["icon"] = "📚"

            try:
                article_model.create(vals)
                _logger.info("Installed documentation for module: %s", self.name)
            except Exception as e:
                _logger.error(
                    "Failed to create documentation for %s: %s",
                    self.name,
                    e,
                )

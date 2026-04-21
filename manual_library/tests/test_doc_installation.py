# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.tagged("post_install", "-at_install")
class TestManualDocInstallation(odoo.tests.common.TransactionCase):
    def test_01_documentation_auto_installation(self):
        # [@ANCHOR: test_manual_doc_auto_install]
        # Tests [@ANCHOR: manual_doc_auto_install]
        # Tests [@ANCHOR: story_manual_doc_installation]
        # Tests [@ANCHOR: journey_developer_integration]
        """
        Verify that the _install_all_module_documentation method correctly
        discovers and installs documentation from modules.
        """
        # Since manual_library itself has documentation, we can check if it's installed.
        title = "Manual Library Documentation"

        # We search for the article
        article = self.env["knowledge.article"].search([("name", "=", title)], limit=1)

        # If it's not found, we manually trigger the installation to verify the logic
        if not article:
            # Mock the service account to return the current user for the test scope.
            from unittest.mock import patch # noqa: E402
            with patch('odoo.addons.zero_sudo.models.security_utils.ZeroSudoSecurityUtils._get_service_uid', return_value=self.env.uid):
                self.env["ir.module.module"]._install_all_module_documentation()
            article = self.env["knowledge.article"].search([("name", "=", title)], limit=1)

        self.assertTrue(article, "Documentation for manual_library should be installed.")

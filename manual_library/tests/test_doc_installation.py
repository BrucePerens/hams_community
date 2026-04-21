# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.tagged("post_install", "-at_install")
class TestManualDocInstallation(odoo.tests.common.TransactionCase):
    def test_01_documentation_auto_installation(self):
        # [@ANCHOR: test_zero_sudo_doc_installer]
        # Tests [@ANCHOR: zero_sudo_doc_installer]
        # Tests [@ANCHOR: story_zero_sudo_doc_installer]
        # Tests [@ANCHOR: journey_developer_integration]
        """
        Verify that the _bootstrap_knowledge_docs method correctly
        discovers and installs documentation from modules.
        """
        title = "Manual Library Documentation"
        article = self.env["knowledge.article"].search([("name", "=", title)], limit=1)

        if not article:
            from unittest.mock import patch # noqa: E402
            with patch('odoo.addons.zero_sudo.models.security_utils.ZeroSudoSecurityUtils._get_service_uid', return_value=self.env.uid):
                self.env["ir.module.module"]._bootstrap_knowledge_docs()
            article = self.env["knowledge.article"].search([("name", "=", title)], limit=1)

        self.assertTrue(article, "Documentation for manual_library should be installed.")

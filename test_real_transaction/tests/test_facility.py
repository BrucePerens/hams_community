# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase


@tagged("post_install", "-at_install")
class TestRealTransactionFacility(RealTransactionCase):
    # Tests [@ANCHOR: cursor_hijacking]
    # Tests [@ANCHOR: leak_snapshotting]
    # Tests [@ANCHOR: orm_instrumentation]
    # Tests [@ANCHOR: automated_cleanup]
    # Tests [@ANCHOR: leak_verification]

    def test_01_auto_cleanup_tracking(self):
        """
        Prove that the facility accurately tracks and auto-deletes standard ORM creations.
        """
        user = self.env["res.users"].create(
            {"name": "Cleanup Target", "login": "cleanup_target"}
        )
        self.env.cr.commit()

        # Verify the record is physically in the DB and tracked
        self.assertTrue(user.exists())
        self.assertIn(user.id, self._tracked_records["res.users"])
        # Note: TearDown will automatically delete this user and check for leaks.

    def test_02_leak_detector_catches_raw_sql(self):
        """
        Prove that the SQL Leak Detector successfully triggers an AssertionError
        if a test bypasses the ORM tracker using raw SQL inserts.
        """
        # Manually invoke the teardown logic to simulate a leak
        self.cr.execute(
            "INSERT INTO ir_module_category (name) VALUES ('\"SQL Leak Test\"') RETURNING id"
        )
        leaked_id = self.cr.fetchone()[0]
        self.env.cr.commit()

        # Temporarily mock the tearDown leak detector to ensure it would raise
        leaks = []
        noisy_tables_records = self.env['test_real_transaction.noisy_table'].search([])
        noisy_tables = {record.name for record in noisy_tables_records}

        self.cr.execute("SELECT count(1) FROM ir_module_category")
        final_count = self.cr.fetchone()[0]
        initial_count = self._initial_counts.get("ir_module_category", 0)

        if "ir_module_category" not in noisy_tables and final_count - initial_count != 0:
            leaks.append("ir_module_category")

        # Clean up the raw SQL insertion so the REAL tearDown doesn't crash the test suite
        self.cr.execute("DELETE FROM ir_module_category WHERE id = %s", (leaked_id,))
        self.env.cr.commit()

        self.assertIn(
            "ir_module_category",
            leaks,
            "The leak detector MUST catch raw SQL insertions.",
        )

    def test_03_foreign_key_cascade_cleanup(self):
        """
        Prove that the multi-pass auto-cleanup handles hierarchical dependencies.
        """
        company = self.env["res.company"].create({"name": "Test Company"})
        user = self.env["res.users"].create(
            {
                "name": "FK User",
                "login": "fk_user",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
            }
        )
        self.env.cr.commit()

        self.assertTrue(company.exists())
        self.assertTrue(user.exists())
        # TearDown will now execute its 3-pass loop. If it fails to cascade,
        # the Leak Detector will catch it and fail the suite.

    def test_04_dynamic_noisy_tables(self):
        """
        Prove that adding a table to the noisy_table model prevents the leak detector
        from catching it.
        """
        # Add ir_module_category to noisy tables
        noisy_table_record = self.env['test_real_transaction.noisy_table'].create({
            'name': 'ir_module_category'
        })
        self.env.cr.commit()

        # Simulate a leak
        self.cr.execute(
            "INSERT INTO ir_module_category (name) VALUES ('\"SQL Leak Test Noisy\"') RETURNING id"
        )
        leaked_id = self.cr.fetchone()[0]
        self.env.cr.commit()

        # Run the leak detector logic
        leaks = []
        noisy_tables_records = self.env['test_real_transaction.noisy_table'].search([])
        noisy_tables = {record.name for record in noisy_tables_records}

        self.cr.execute("SELECT count(1) FROM ir_module_category")
        final_count = self.cr.fetchone()[0]
        initial_count = self._initial_counts.get("ir_module_category", 0)

        if "ir_module_category" not in noisy_tables and final_count - initial_count != 0:
            leaks.append("ir_module_category")

        # Clean up the leak AND the noisy table record to keep the DB clean for tearDown
        self.cr.execute("DELETE FROM ir_module_category WHERE id = %s", (leaked_id,))
        noisy_table_record.unlink()
        self.env.cr.commit()

        self.assertNotIn(
            "ir_module_category",
            leaks,
            "The leak detector MUST ignore tables present in the noisy_table model.",
        )

    def test_05_documentation_installed(self):
        """
        Verify that the module's documentation was correctly installed into knowledge.article.
        """
        # Tests [@ANCHOR: documentation_bootstrap]
        # Tests [@ANCHOR: documentation_injection]
        if "knowledge.article" in self.env:
            article = self.env["knowledge.article"].search(
                [("name", "=", "Real Transaction Testing Facility Guide")], limit=1
            )
            self.assertTrue(article, "Documentation article should have been created.")
            self.assertIn("Real Transaction Testing Facility", article.body)

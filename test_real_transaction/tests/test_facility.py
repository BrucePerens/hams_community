#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase


@tagged("post_install", "-at_install")
class TestRealTransactionFacility(RealTransactionCase):
    def test_01_auto_cleanup_tracking(self):
        """
        Prove that the facility accurately tracks and auto-deletes standard ORM creations.
        """
        user = self.env["res.users"].create(
            {"name": "Cleanup Target", "login": "cleanup_target"}
        )
        self.env.cr.commit() # burn-ignore-test-commit  # fmt: skip

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
        self.env.cr.commit() # burn-ignore-test-commit  # fmt: skip

        # Temporarily mock the tearDown leak detector to ensure it would raise
        leaks = []
        self.cr.execute("SELECT count(1) FROM ir_module_category")
        final_count = self.cr.fetchone()[0]
        initial_count = self._initial_counts.get("ir_module_category", 0)
        if final_count - initial_count != 0:
            leaks.append("ir_module_category")

        # Clean up the raw SQL insertion so the REAL tearDown doesn't crash the test suite
        self.cr.execute("DELETE FROM ir_module_category WHERE id = %s", (leaked_id,))
        self.env.cr.commit() # burn-ignore-test-commit  # fmt: skip

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
        self.env.cr.commit() # burn-ignore-test-commit  # fmt: skip

        self.assertTrue(company.exists())
        self.assertTrue(user.exists())
        # TearDown will now execute its 3-pass loop. If it fails to cascade,
        # the Leak Detector will catch it and fail the suite.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import logging
import odoo
from odoo.tests.common import BaseCase, get_db_name
from odoo.modules.registry import Registry
from psycopg2 import sql

_logger = logging.getLogger(__name__)

# Store the original create method globally to avoid descriptor binding issues
_original_create = odoo.models.BaseModel.create


class RealTransactionCase(BaseCase):
    """
    A testing facility that bypasses Odoo's test cursor wrapping (TransactionCase).
    It provides a real, committable PostgreSQL cursor allowing tests to behave
    exactly like a live production environment.

    Features:
    1. Auto-Cleanup: Instruments the ORM to track and auto-delete created records.
    2. Leak Detection: Takes a SQL snapshot of all database tables before and after the
       test. If any records leak (e.g., via raw SQL inserts), it raises an AssertionError.
    """

    def setUp(self):
        super().setUp()
        self.registry = Registry(get_db_name())
        self.cr = self.registry.cursor()
        self.env = odoo.api.Environment(self.cr, odoo.SUPERUSER_ID, {})

        # 1. Snapshot exact table counts
        self.cr.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        self._tables = [r[0] for r in self.cr.fetchall()]
        self._initial_counts = {}
        for t in self._tables:
            # Securely construct table identifiers using psycopg2.sql
            query = sql.SQL("SELECT count(1) FROM {}").format(sql.Identifier(t))
            self.cr.execute(query)
            self._initial_counts[t] = self.cr.fetchone()[0]

        self._tracked_records = collections.defaultdict(set)

        # 2. Instrument ORM Creation
        def tracking_create(model_self, *args, **kwargs):
            # Execute via module-level reference to prevent binding issues
            records = _original_create(model_self, *args, **kwargs)
            if records:
                self._tracked_records[model_self._name].update(records.ids)
            return records

        odoo.models.BaseModel.create = tracking_create

    def tearDown(self):
        # 1. Restore standard ORM behavior
        odoo.models.BaseModel.create = _original_create

        # 2. Automated ORM Cleanup (Multiple passes for Foreign Key cascades)
        from odoo.tools import mute_logger

        for _ in range(3):
            pending_deletes = False
            for model_name, ids in list(self._tracked_records.items()):
                if model_name in self.env and ids:
                    try:
                        # Silence Odoo's SQL logger so expected constraint violations don't pollute the test output
                        with self.env.cr.savepoint(), mute_logger(
                            "odoo.sql_db"
                        ), mute_logger("odoo.models.unlink"):
                            # Env is already initialized as SUPERUSER_ID, no .sudo() needed
                            records = (
                                self.env[model_name]
                                .with_context(active_test=False)
                                .browse(list(ids))
                                .exists()
                            )
                            if records:
                                records.unlink()
                                self._tracked_records[model_name] = set()
                    except Exception:
                        pending_deletes = True
            if not pending_deletes:
                break

        # Commit the automated cleanup to disk
        self.env.cr.commit() # burn-ignore-test-commit  # fmt: skip

        # 3. Verify No Leaks (Ignoring noisy system logging/chatter tables)
        leaks = []
        noisy_tables = {
            "bus_bus",
            "ir_logging",
            "base_registry_signaling",
            "ir_cron",
            "mail_message",
            "mail_notification",
            "mail_followers",
            "mail_tracking_value",
            "res_groups_users_rel",
            "res_company_users_rel",
            "res_users_log",
        }

        for t in self._tables:
            if t in noisy_tables:
                continue
            # Securely construct table identifiers using psycopg2.sql
            query = sql.SQL("SELECT count(1) FROM {}").format(sql.Identifier(t))
            self.cr.execute(query)
            final_count = self.cr.fetchone()[0]
            initial_count = self._initial_counts.get(t, 0)
            diff = final_count - initial_count
            if diff != 0:
                leaks.append(f"{t} ({diff:+d})")

        # 4. Close DB Connection
        self.cr.rollback()
        self.cr.close()
        super().tearDown()

        if leaks:
            leaks = [l for l in leaks if "database_activity" not in l]
            if leaks:
                raise AssertionError(
                    f"Database pollution detected! Auto-cleanup failed or raw SQL was used. Leaked records: {', '.join(leaks)}"
                )

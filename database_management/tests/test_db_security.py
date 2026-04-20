# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged("post_install", "-at_install")
class TestDbSecurity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.admin = self.env.ref("base.user_admin")
        self.db_manager = self.env["res.users"].create(
            {
                "name": "DB Manager",
                "login": "db_manager",
                "group_ids": [
                    (4, self.env.ref("database_management.group_database_management_manager").id),
                    (4, self.env.ref("base.group_user").id),
                ],
            }
        )
        self.user_std = self.env["res.users"].create(
            {
                "name": "Std",
                "login": "std_db",
                "group_ids": [(4, self.env.ref("base.group_portal").id)],
            }
        )

        web_grp = self.env.ref(
            "user_websites.group_user_websites_user", raise_if_not_found=False
        )
        groups_web = [self.env.ref("base.group_portal").id] + (
            [web_grp.id] if web_grp else []
        )
        self.user_web = self.env["res.users"].create(
            {"name": "Web", "login": "web_db", "group_ids": [(6, 0, groups_web)]}
        )

        ham_grp = self.env.ref("base.group_portal", raise_if_not_found=False)
        groups_ham = [self.env.ref("base.group_portal").id] + (
            [ham_grp.id] if ham_grp else []
        )
        self.user_ham = self.env["res.users"].create(
            {"name": "Ham", "login": "ham_db", "group_ids": [(6, 0, groups_ham)]}
        )

        swl_grp = self.env.ref("base.group_portal", raise_if_not_found=False)
        groups_swl = [self.env.ref("base.group_portal").id] + (
            [swl_grp.id] if swl_grp else []
        )
        self.user_swl = self.env["res.users"].create(
            {"name": "Swl", "login": "swl_db", "group_ids": [(6, 0, groups_swl)]}
        )

        self.public_user = self.env.ref("base.public_user")

        # Fetch existing SQL View records for testing read isolation
        self.table_stat = (
            self.env["database.table.stat"].with_user(self.db_manager).search([], limit=1)
        )
        self.pg_setting = (
            self.env["database.pg.setting"].with_user(self.db_manager).search([], limit=1)
        )

    def test_01_multi_persona_isolation(self):
        """
        BDD: Given ADR-0050 Proxy Ownership IDOR (Multi-Persona Mandate)
        When standard personas attempt to interact with the database APM tools
        Then they MUST be violently rejected by the ORM, as only Database Managers have access.
        """
        # First, verify that the DB Manager CAN access the tools
        if self.table_stat:
            self.table_stat.with_user(self.db_manager).read(["table_name"])
        if self.pg_setting:
            self.pg_setting.with_user(self.db_manager).read(["name"])

        self.env["pg.optimize.wizard"].with_user(self.db_manager).create({"ram_gb": 16})
        self.env["pg.ha.wizard"].with_user(self.db_manager).create({"primary_ip": "10.0.0.1"})

        for user in [
            self.user_std,
            self.user_web,
            self.user_ham,
            self.user_swl,
            self.public_user,
        ]:
            # Assert SQL Views are protected
            if self.table_stat:
                with self.assertRaises(
                    AccessError,
                    msg=f"{user.name} MUST NOT be able to read DB table stats.",
                ):
                    self.table_stat.with_user(user).read(["table_name"])
            if self.pg_setting:
                with self.assertRaises(
                    AccessError,
                    msg=f"{user.name} MUST NOT be able to read PG configurations.",
                ):
                    self.pg_setting.with_user(user).read(["name"])

            # Assert Wizards are protected
            with self.assertRaises(
                AccessError,
                msg=f"{user.name} MUST NOT be able to access the Optimize Wizard.",
            ):
                self.env["pg.optimize.wizard"].with_user(user).create({"ram_gb": 16})

            with self.assertRaises(
                AccessError,
                msg=f"{user.name} MUST NOT be able to access the HA Wizard.",
            ):
                self.env["pg.ha.wizard"].with_user(user).create(
                    {"primary_ip": "10.0.0.1"}
                )

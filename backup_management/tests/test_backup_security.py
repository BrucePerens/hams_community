# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged("post_install", "-at_install")
class TestBackupSecurity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.admin = self.env.ref("base.user_admin")
        self.user_std = self.env["res.users"].create(
            {
                "name": "Std",
                "login": "std_backup",
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
            {"name": "Web", "login": "web_backup", "group_ids": [(6, 0, groups_web)]}
        )

        ham_grp = self.env.ref("base.group_portal", raise_if_not_found=False)
        groups_ham = [self.env.ref("base.group_portal").id] + (
            [ham_grp.id] if ham_grp else []
        )
        self.user_ham = self.env["res.users"].create(
            {"name": "Ham", "login": "ham_backup", "group_ids": [(6, 0, groups_ham)]}
        )

        swl_grp = self.env.ref("base.group_portal", raise_if_not_found=False)
        groups_swl = [self.env.ref("base.group_portal").id] + (
            [swl_grp.id] if swl_grp else []
        )
        self.user_swl = self.env["res.users"].create(
            {"name": "Swl", "login": "swl_backup", "group_ids": [(6, 0, groups_swl)]}
        )

        self.public_user = self.env.ref("base.public_user")

        self.config = (
            self.env["backup.config"]
            .with_user(self.admin)
            .create({"name": "Sec Test", "engine": "kopia", "target_path": "/tmp"})
        )
        self.snapshot = (
            self.env["backup.snapshot"]
            .with_user(self.admin)
            .create({"config_id": self.config.id, "snapshot_id": "snap_sec_1"})
        )

    def test_01_multi_persona_isolation(self):
        """
        BDD: Given ADR-0050 Proxy Ownership IDOR (Multi-Persona Mandate)
        When standard personas attempt to interact with the backup tables
        Then they MUST be violently rejected by the ORM, as only Backup Admins have access.
        """
        for user in [
            self.user_std,
            self.user_web,
            self.user_ham,
            self.user_swl,
            self.public_user,
        ]:
            with self.assertRaises(
                AccessError, msg=f"{user.name} MUST NOT be able to read configs."
            ):
                self.config.with_user(user).read(["name"])

            with self.assertRaises(
                AccessError, msg=f"{user.name} MUST NOT be able to write configs."
            ):
                self.config.with_user(user).write({"name": "hacked"})

            with self.assertRaises(
                AccessError, msg=f"{user.name} MUST NOT be able to create configs."
            ):
                self.env["backup.config"].with_user(user).create(
                    {"name": "x", "engine": "kopia", "target_path": "y"}
                )

            with self.assertRaises(
                AccessError, msg=f"{user.name} MUST NOT be able to unlink configs."
            ):
                self.config.with_user(user).unlink()

            with self.assertRaises(
                AccessError, msg=f"{user.name} MUST NOT be able to read snapshots."
            ):
                self.snapshot.with_user(user).read(["snapshot_id"])

    def test_02_service_account_capabilities(self):
        """
        Verify that user_backup_service_internal can perform its duties.
        """
        service_user = self.env.ref("backup_management.user_backup_service_internal")

        # Read configs
        configs = self.env["backup.config"].with_user(service_user).search([])
        self.assertIn(self.config.id, configs.ids)

        # Create snapshots
        snap = (
            self.env["backup.snapshot"]
            .with_user(service_user)
            .create(
                {
                    "config_id": self.config.id,
                    "snapshot_id": "service_snap_1",
                    "status": "completed",
                }
            )
        )
        self.assertTrue(snap.exists())

        # Check binary manifest access (needed for auto-download)
        # We need to ensure binary_downloader is installed or mocked if this test runs in isolation
        if "binary.manifest" in self.env:
            manifests = self.env["binary.manifest"].with_user(service_user).search([])
            self.assertIsNotNone(manifests)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestBinaryManifest(TransactionCase):
    def test_01_binary_manifest_views(self):
        # [%ANCHOR: test_binary_manifest_views]
        v1 = self.env["zero_sudo.binary.manifest"].get_view(view_type="list")
        self.assertIn("name", v1["arch"])
        v2 = self.env["zero_sudo.binary.manifest"].get_view(view_type="form")
        self.assertIn("url", v2["arch"])

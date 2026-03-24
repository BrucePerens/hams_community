#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import os
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.request
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class BinaryManifest(models.Model):
    _name = "binary.manifest"
    _description = "Binary Download Manifest"

    name = fields.Char(
        string="Binary Name", required=True, help="Command name (e.g., kopia)"
    )
    url = fields.Char(string="Download URL", required=True)
    checksum = fields.Char(string="SHA-256 Checksum", required=True)
    archive_type = fields.Selection(
        [("binary", "Raw Binary"), ("tar.gz", "Tarball (.tar.gz)")],
        string="Archive Type",
        default="binary",
        required=True,
    )
    extract_member = fields.Char(
        string="Extract Member", help="Specific file to extract from the archive."
    )

    _name_uniq = models.Constraint("UNIQUE(name)", "The binary name must be unique!")
    _name_not_empty = models.Constraint(
        "CHECK(LENGTH(TRIM(name)) > 0)", "The binary name cannot be empty."
    )
    _url_not_empty = models.Constraint(
        "CHECK(LENGTH(TRIM(url)) > 0)", "The download URL cannot be empty."
    )
    _chksum_not_empty = models.Constraint(
        "CHECK(LENGTH(TRIM(checksum)) > 0)", "The checksum cannot be empty."
    )

    @api.model
    def ensure_executable(self, cmd_name):
        path = shutil.which(cmd_name)
        if path:
            return path

        manifest_record = self.env["binary.manifest"].search(
            [("name", "=", cmd_name)], limit=1
        )
        if not manifest_record:
            raise UserError(
                _(
                    "Missing dependency: '%s'. Please configure it in Settings -> Technical -> Binary Manifests or install via OS package manager."
                )
                % cmd_name
            )

        if platform.system() != "Linux" or platform.machine() != "x86_64":
            raise UserError(
                _(
                    "Auto-install of %s is only supported on Linux x86_64. Please install manually."
                )
                % cmd_name
            )

        data_dir = tools.config.get("data_dir", "/var/lib/odoo")
        bin_dir = os.path.join(data_dir, "hams_bin")

        os.makedirs(bin_dir, exist_ok=True)
        os.chmod(bin_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

        target_bin = os.path.join(bin_dir, cmd_name)

        if os.path.exists(target_bin):
            os.chmod(target_bin, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            return target_bin

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                urllib.request.urlretrieve(manifest_record.url, tmp.name)

            hasher = hashlib.sha256()
            with open(tmp.name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)

            if hasher.hexdigest() != manifest_record.checksum:
                os.unlink(tmp.name)
                raise UserError(
                    _("Security Alert: Checksum mismatch for downloaded %s binary.")
                    % cmd_name
                )

            if manifest_record.archive_type == "tar.gz":
                with tarfile.open(tmp.name, "r:gz") as tar:
                    for member in tar.getmembers():
                        extract_target = manifest_record.extract_member or cmd_name
                        if (
                            member.name.endswith(f"/{extract_target}")
                            or member.name == extract_target
                        ):
                            member.name = cmd_name
                            tar.extract(member, path=bin_dir)
                            break
            else:
                shutil.copy2(tmp.name, target_bin)

            os.chmod(target_bin, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            os.unlink(tmp.name)
            return target_bin
        except Exception as e:
            raise UserError(_("Failed to auto-install %s: %s") % (cmd_name, str(e)))

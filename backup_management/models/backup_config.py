import json
import subprocess
import os
import datetime
import shutil
import platform
import urllib.request
import tarfile
import tempfile
import odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None


KOPIA_CHECKSUM = "6eb5cc175ccf2b38038bf34710184b251ce7c77f013bd33816650db8182742dd"

class BackupConfig(models.Model):
    _name = "backup.config"
    _description = "Backup Configuration"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=True)
    engine = fields.Selection(
        [("kopia", "Kopia"), ("pgbackrest", "pgBackRest")], required=True
    )
    target_path = fields.Char(
        string="Target / Stanza",
        required=True,
        help="Repository path for Kopia, or Stanza name for pgBackRest.",
    )
    minimum_size_mb = fields.Integer(
        string="Minimum Size (MB)",
        default=0,
        help="Triggers a Pager Duty alert if a new snapshot is smaller than this.",
    )

    kopia_password_crypt = fields.Char(string="Encrypted Kopia Password")
    kopia_password = fields.Char(
        string="Kopia Password",
        compute="_compute_kopia_password",
        inverse="_inverse_kopia_password",
    )

    storage_type = fields.Selection(
        [("local", "Local Directory"), ("s3", "AWS S3"), ("b2", "Backblaze B2")],
        default="local",
        string="Storage Type",
    )
    bucket_name = fields.Char(string="Bucket Name")
    endpoint_url = fields.Char(string="Endpoint URL")
    access_key = fields.Char(string="Access Key")
    secret_key_crypt = fields.Char(string="Encrypted Secret Key")
    secret_key = fields.Char(
        string="Secret Key",
        compute="_compute_secret_key",
        inverse="_inverse_secret_key",
    )

    keep_daily = fields.Integer(string="Keep Daily", default=7)
    keep_weekly = fields.Integer(string="Keep Weekly", default=4)
    keep_monthly = fields.Integer(string="Keep Monthly", default=6)
    exclude_patterns = fields.Text(
        string="Exclude Patterns (.kopiaignore)", help="One pattern per line."
    )

    restore_drill_script = fields.Char(
        string="Automated Restore Drill Script",
        help="Absolute path to a shell script that performs a test restore and data validation.",
    )
    last_drill_time = fields.Datetime(string="Last Successful Drill", readonly=True)

    snapshot_ids = fields.One2many("backup.snapshot", "config_id", string="Snapshots")

    def _get_fernet(self):
        key = os.environ.get("HAMS_CRYPTO_KEY")
        if key and Fernet:
            return Fernet(key.encode("utf-8"))
        return None

    @api.depends("kopia_password_crypt")
    def _compute_kopia_password(self):
        f = self._get_fernet()
        for rec in self:
            if rec.kopia_password_crypt and f:
                try:
                    rec.kopia_password = f.decrypt(
                        rec.kopia_password_crypt.encode("utf-8")
                    ).decode("utf-8")
                except Exception:
                    rec.kopia_password = "***DECRYPT_FAILED***"
            else:
                rec.kopia_password = False

    def _inverse_kopia_password(self):
        f = self._get_fernet()
        for rec in self:
            if rec.kopia_password and f:
                rec.kopia_password_crypt = f.encrypt(
                    rec.kopia_password.encode("utf-8")
                ).decode("utf-8")
            else:
                rec.kopia_password_crypt = False

    @api.depends("secret_key_crypt")
    def _compute_secret_key(self):
        f = self._get_fernet()
        for rec in self:
            if rec.secret_key_crypt and f:
                try:
                    rec.secret_key = f.decrypt(
                        rec.secret_key_crypt.encode("utf-8")
                    ).decode("utf-8")
                except Exception:
                    rec.secret_key = "***DECRYPT_FAILED***"
            else:
                rec.secret_key = False

    def _inverse_secret_key(self):
        f = self._get_fernet()
        for rec in self:
            if rec.secret_key and f:
                rec.secret_key_crypt = f.encrypt(rec.secret_key.encode("utf-8")).decode(
                    "utf-8"
                )
            else:
                rec.secret_key_crypt = False

    def _get_executable(self, engine):
        cmd_path = shutil.which(engine)
        if cmd_path:
            return cmd_path

        if engine == "pgbackrest":
            raise UserError(
                _(
                    "pgBackRest is missing. It requires OS-level PostgreSQL dependencies and must be installed via your package manager (e.g., 'sudo apt-get install pgbackrest')."
                )
            )

        if engine == "kopia":
            if platform.system() != "Linux" or platform.machine() != "x86_64":
                raise UserError(
                    _(
                        "Auto-install of Kopia is only supported on Linux x86_64. Please install manually."
                    )
                )

            data_dir = odoo.tools.config.get("data_dir", "/var/lib/odoo")
            bin_dir = os.path.join(data_dir, "hams_bin")
            os.makedirs(bin_dir, exist_ok=True)
            kopia_bin = os.path.join(bin_dir, "kopia")

            if os.path.exists(kopia_bin):
                return kopia_bin

            url = "https://github.com/kopia/kopia/releases/download/v0.18.2/kopia-0.18.2-linux-x64.tar.gz"
            try:
                import hashlib
                msg_body = _("Kopia binary not found. Auto-downloading static binary from GitHub...")
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_orchestration]  # fmt: skip
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp:
                    urllib.request.urlretrieve(url, tmp.name)

                expected_hash = KOPIA_CHECKSUM
                hasher = hashlib.sha256()
                with open(tmp.name, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                if hasher.hexdigest() != expected_hash:
                    os.unlink(tmp.name)
                    raise UserError(_("Security Alert: Checksum mismatch for downloaded Kopia binary."))

                with tarfile.open(tmp.name, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.name.endswith("/kopia") or member.name == "kopia":
                            member.name = "kopia"
                            tar.extract(member, path=bin_dir)
                            break
                os.chmod(kopia_bin, 0o755)
                os.unlink(tmp.name)
                msg_body = _("Kopia successfully installed to %s") % kopia_bin
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_orchestration]  # fmt: skip
                return kopia_bin
            except Exception as e:
                raise UserError(_("Failed to auto-install Kopia: %s") % str(e))

        raise UserError(_("Unknown engine: %s") % engine)

    def action_trigger_backup(self):
        # [%ANCHOR: backup_trigger_execution]
        for rec in self:
            if rec.engine == "kopia":
                rec._trigger_kopia_backup()
            elif rec.engine == "pgbackrest":
                rec._trigger_pgbackrest_backup()
        return True

    def action_apply_policies(self):
        # [%ANCHOR: backup_apply_policies]
        for rec in self:
            if rec.engine == "kopia":
                rec._apply_kopia_policies()
        return True

    def _trigger_kopia_backup(self):
        try:
            exe = self._get_executable("kopia")
            env_vars = os.environ.copy()
            if self.kopia_password:
                env_vars["KOPIA_PASSWORD"] = self.kopia_password
            res = subprocess.run(
                [exe, "snapshot", "create", self.target_path, "--json"],
                capture_output=True,
                text=True,
                timeout=3600,
                env=env_vars,
                shell=False,
            )
            if res.returncode != 0:
                self._report_backup_failure(f"Kopia backup failed: {res.stderr}")
            else:
                msg_body = _("Kopia backup completed successfully.")
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_orchestration]  # fmt: skip
                self.action_sync_snapshots()
        except Exception as e:
            self._report_backup_failure(f"Error triggering Kopia: {e}")

    def _trigger_pgbackrest_backup(self):
        try:
            exe = self._get_executable("pgbackrest")
            cmd = [exe, "backup", f"--stanza={self.target_path}", "--type=full"]
            if self.keep_daily > 0:
                cmd.append(f"--repo1-retention-full={self.keep_daily}")
            res = subprocess.run(
                cmd, capture_output=True, text=True, timeout=3600, shell=False
            )
            if res.returncode != 0:
                self._report_backup_failure(f"pgBackRest backup failed: {res.stderr}")
            else:
                msg_body = _("pgBackRest backup completed successfully.")
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_orchestration]  # fmt: skip
                self.action_sync_snapshots()
        except Exception as e:
            self._report_backup_failure(f"Error triggering pgBackRest: {e}")

    def _apply_kopia_policies(self):
        try:
            exe = self._get_executable("kopia")
            env_vars = os.environ.copy()
            if self.kopia_password:
                env_vars["KOPIA_PASSWORD"] = self.kopia_password
            cmd = [exe, "policy", "set", self.target_path]
            cmd.extend(
                [
                    f"--keep-latest={self.keep_daily}",
                    f"--keep-daily={self.keep_daily}",
                    f"--keep-weekly={self.keep_weekly}",
                    f"--keep-monthly={self.keep_monthly}",
                ]
            )
            if self.exclude_patterns:
                for line in self.exclude_patterns.splitlines():
                    if line.strip():
                        cmd.append(f"--add-ignore={line.strip()}")
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env_vars,
                shell=False,
            )
            if res.returncode != 0:
                self._report_backup_failure(f"Kopia policy set failed: {res.stderr}")
            else:
                msg_body = _("Kopia policies applied successfully.")
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_orchestration]  # fmt: skip
        except Exception as e:
            self._report_backup_failure(f"Error applying Kopia policy: {e}")

    def _report_backup_failure(self, message):
        # [%ANCHOR: backup_pager_synergy]
        if "pager.incident" in self.env:
            try:
                pager_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
                    "pager_duty.user_pager_service_internal"
                )
                self.env["pager.incident"].with_user(pager_uid).report_incident(
                    {
                        "source": f"Backup Manager: {self.name}",
                        "severity": "critical",
                        "description": message,
                    }
                )
            except Exception:
                pass
        self.message_post(body=message) # audit-ignore-mail: Tested by [%ANCHOR: backup_pager_synergy]  # fmt: skip

    @api.model
    def get_board_data(self):
        # [%ANCHOR: backup_board_data]
        configs = self.search_read([], ["name", "engine", "target_path"])
        now = fields.Datetime.now()
        for c in configs:
            snap = self.env["backup.snapshot"].search_read(
                [("config_id", "=", c["id"])],
                ["snapshot_id", "start_time", "size_bytes", "status"],
                order="start_time desc",
                limit=1,
            )
            if snap:
                c["latest_snapshot"] = snap[0]
                delta = (
                    (now - snap[0]["start_time"]).total_seconds()
                    if snap[0]["start_time"]
                    else 999999
                )
                c["is_stale"] = delta > (26 * 60 * 60)
            else:
                c["latest_snapshot"] = False
                c["is_stale"] = True
        return configs

    def action_sync_snapshots(self):
        # [%ANCHOR: backup_sync_kopia]
        # [%ANCHOR: backup_sync_pgbackrest]
        for rec in self:
            if rec.engine == "kopia":
                rec._sync_kopia()
            elif rec.engine == "pgbackrest":
                rec._sync_pgbackrest()
        return True

    def _sync_kopia(self):
        try:
            exe = self._get_executable("kopia")
            env_vars = os.environ.copy()
            if self.kopia_password:
                env_vars["KOPIA_PASSWORD"] = self.kopia_password

            res = subprocess.run(
                [exe, "snapshot", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                env=env_vars,
                shell=False,
            )
            if res.returncode != 0:
                self._report_backup_failure(f"Kopia sync failed: {res.stderr}")
                return

            data = json.loads(res.stdout)
            self._process_snapshot_data(data, "kopia")
        except Exception as e:
            self._report_backup_failure(f"Error running Kopia: {e}")

    def _sync_pgbackrest(self):
        try:
            exe = self._get_executable("pgbackrest")
            res = subprocess.run(
                [exe, "info", f"--stanza={self.target_path}", "--output=json"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
            )
            if res.returncode != 0:
                self._report_backup_failure(f"pgBackRest sync failed: {res.stderr}")
                return

            data = json.loads(res.stdout)
            self._process_snapshot_data(data, "pgbackrest")
        except Exception as e:
            self._report_backup_failure(f"Error running pgBackRest: {e}")

    def _process_snapshot_data(self, data, engine):
        Snapshot = self.env["backup.snapshot"]
        existing_snaps = Snapshot.search([("config_id", "=", self.id)], limit=5000)
        existing_map = {s.snapshot_id: s for s in existing_snaps}

        creates = []
        if engine == "kopia":
            for snap in data:
                sid = snap.get("id")
                if sid and sid not in existing_map:
                    creates.append(
                        {
                            "config_id": self.id,
                            "snapshot_id": sid,
                            "start_time": snap.get("startTime", "")[:19].replace(
                                "T", " "
                            ),
                            "size_bytes": snap.get("summary", {}).get("totalBytes", 0),
                            "status": "completed",
                        }
                    )
        elif engine == "pgbackrest":
            for stanza in data:
                for snap in stanza.get("backup", []):
                    sid = snap.get("label")
                    if sid and sid not in existing_map:
                        ts = snap.get("timestamp", {}).get("start", 0)
                        dt = (
                            datetime.datetime.utcfromtimestamp(ts).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            if ts
                            else False
                        )
                        creates.append(
                            {
                                "config_id": self.id,
                                "snapshot_id": sid,
                                "start_time": dt,
                                "size_bytes": snap.get("info", {}).get("size", 0),
                                "status": "completed",
                            }
                        )

        if creates:
            Snapshot.create(creates)
            if self.minimum_size_mb > 0:
                for c in creates:
                    snap_mb = c.get("size_bytes", 0) / (1024 * 1024)
                    if snap_mb < self.minimum_size_mb:
                        self._report_backup_failure(
                            f"Snapshot Anomaly: Snapshot {c.get('snapshot_id')} is {snap_mb:.2f} MB, below the {self.minimum_size_mb} MB minimum."
                        )

    @api.model
    def cron_sync_all_backups(self):
        # [%ANCHOR: cron_sync_all_backups]
        configs = self.env["backup.config"].search([], limit=1000)
        now = fields.Datetime.now()
        for conf in configs:
            conf.action_sync_snapshots()

            snaps = conf.snapshot_ids.sorted(lambda s: s.start_time, reverse=True)
            latest_snap = snaps[0] if snaps else None
            if latest_snap and latest_snap.start_time:
                delta = (now - latest_snap.start_time).total_seconds()
                if delta > (
                    26 * 60 * 60
                ):  # 26 hours (allows for 24h cron jitter without false positives)
                    conf._report_backup_failure(
                        f"Stale Backup Alert: No new snapshots detected for {conf.name} in over 26 hours."
                    )

            if conf.restore_drill_script:
                delta_drill = (
                    (now - conf.last_drill_time).total_seconds()
                    if conf.last_drill_time
                    else 9999999
                )
                if delta_drill > (7 * 24 * 60 * 60):  # 7 Days
                    conf._execute_restore_drill()

        self.env.ref("backup_management.cron_sync_backups")._trigger()

    def _execute_restore_drill(self):
        try:
            res = subprocess.run(
                [self.restore_drill_script],
                capture_output=True,
                text=True,
                timeout=7200,
                shell=False,
            )
            if res.returncode != 0:
                self._report_backup_failure(
                    f"Automated Restore Drill FAILED: {res.stderr}"
                )
            else:
                self.last_drill_time = fields.Datetime.now()
                msg_body = _("Automated Restore Drill completed successfully.")
                self.message_post(body=msg_body)  # audit-ignore-mail: Tested by [%ANCHOR: test_backup_cron]  # fmt: skip
        except Exception as e:
            self._report_backup_failure(f"Error triggering Restore Drill: {e}")

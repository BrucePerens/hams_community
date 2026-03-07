import uuid
import json
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.distributed_redis_cache.redis_cache import distributed_cache, invalidate_model_cache

try:
    import yaml
except ImportError:
    yaml = None


class PagerCheck(models.Model):
    _name = "pager.check"
    _description = "Graphical Pager Duty Check"
    _order = "name asc"

    name = fields.Char(string="Check Name / Source", required=True)
    status = fields.Selection(
        [
            ("passing", "Passing"),
            ("failing", "Failing"),
            ("maintenance", "Maintenance"),
        ],
        string="Status",
        default="passing",
        readonly=True,
    )
    last_run = fields.Datetime(string="Last Run", readonly=True)
    check_type = fields.Selection(
        [
            ("system", "System Resource (Disk/RAM/CPU/IO)"),
            ("dns", "DNS Resolution"),
            ("http", "HTTP(S) Endpoint"),
            ("http3", "HTTP/3 (QUIC) Endpoint"),
            ("tcp", "TCP Socket"),
            ("udp", "UDP Datagram"),
            ("redis", "Redis Server (Ping)"),
            ("rabbitmq", "RabbitMQ Server (AMQP)"),
            ("xmlrpc", "XML-RPC Method"),
            ("jsonrpc", "JSON-RPC Method"),
            ("postgres", "PostgreSQL DB (Ping)"),
            ("log", "Log File Tail"),
            ("ssl", "SSL/TLS Certificate Expiry"),
            ("anomaly", "Anomaly Detection (SQL Baseline)"),
            ("synthetic", "Synthetic Journey (Script)"),
            ("certbot", "Certbot Readiness / Dry-Run"),
            ("pg_dump", "PostgreSQL Backup (Dry-Run)"),
            ("nginx", "Nginx Config (Syntax Check)"),
            ("logrotate", "Logrotate (Dry-Run)"),
            ("cloudflared", "Cloudflare Tunnel (Pre-Flight)"),
            ("smtp_dryrun", "SMTP Login (Dry-Run)"),
            ("icmp", "ICMP Ping"),
            ("heartbeat", "Heartbeat (Push Monitor)"),
            ("docker", "Docker Container Health"),
            ("file_absent", "File Must Not Exist (e.g. reboot-required)"),
            ("memcached", "Memcached Server (Ping)"),
            ("ssh", "SSH Handshake"),
            ("systemd", "Systemd Service Status"),
            ("ftp", "FTP Login"),
            ("imap", "IMAP Login"),
            ("pop3", "POP3 Login"),
            ("mysql", "MySQL/MariaDB DB (Ping)"),
            ("snmp", "SNMP Get"),
            ("ldap", "LDAP Server"),
            ("ntp", "NTP Server"),
            ("load", "System Load Average"),
        ],
        string="Monitor Type",
        required=True,
    )

    snmp_community = fields.Char(string="SNMP Community", default="public")
    snmp_oid = fields.Char(string="SNMP OID")
    partition = fields.Char(string="Disk Partition", default="/", help="Specific mount point to check for disk usage.")
    warning_threshold = fields.Integer(string="Warning Threshold %")

    target = fields.Char(
        string="Target (Host/URL/File)",
        help="Prefix with ENV: to inject environment variables.",
    )
    port = fields.Integer(string="Port")
    payload_send = fields.Char(string="Send Payload (String)")
    payload_send_hex = fields.Char(string="Send Payload (Hex)")
    payload_expect = fields.Char(string="Expect Output")

    dbname = fields.Char(string="DB Name")
    dbuser = fields.Char(string="Username (DB/SMTP)")
    dbpass = fields.Char(string="Password (DB/SMTP)")
    query = fields.Text(string="SQL Query (Returns Integer)")
    script = fields.Char(string="Shell Script Command")
    rpc_method = fields.Char(string="RPC Method", help="e.g. execute_kw")
    rpc_params = fields.Text(
        string="RPC Params (JSON Array/Dict)",
        help="e.g. ['db', 2, 'pass', 'res.partner', 'search', [[]]]",
    )

    regex = fields.Char(string="Regex Pattern")
    critical_threshold = fields.Integer(string="Critical Threshold %")
    interval = fields.Integer(string="Polling Interval (sec)", default=60)
    grace_period = fields.Integer(
        string="Startup Grace Period (sec)",
        default=0,
        help="Seconds to wait after daemon startup before reporting failures.",
    )
    active = fields.Boolean(default=True)

    parent_check_id = fields.Many2one(
        "pager.check",
        string="Parent Check (Dependency)",
        help="If parent fails, this check is suppressed.",
    )
    maintenance_start = fields.Datetime(string="Maintenance Start")
    maintenance_end = fields.Datetime(string="Maintenance End")
    auto_remediate_script = fields.Char(
        string="Auto-Remediation Script",
        help="Executed locally by daemon if check fails (e.g., /opt/reboot.sh)",
    )

    heartbeat_uuid = fields.Char(
        string="Heartbeat UUID", default=lambda self: str(uuid.uuid4()), readonly=True
    )
    last_heartbeat = fields.Datetime(string="Last Heartbeat", readonly=True)

    @api.model
    @distributed_cache()
    def _get_check_id_by_uuid(self, hb_uuid, override_svc_uid=None):
        if not hb_uuid:
            return False
        svc_uid = override_svc_uid or self.env[
            "zero_sudo.security.utils"
        ]._get_service_uid("pager_duty.user_pager_service_internal")
        check = (
            self.env["pager.check"]
            .with_user(svc_uid)
            .search([("heartbeat_uuid", "=", hb_uuid)], limit=1)
        )
        return check.id if check else False

    def write(self, vals):
        res = super().write(vals)
        invalidate_model_cache(self.env, self._name)
        payload = json.dumps({"model": self._name})
        self.env.cr.execute("SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload))
        return res

    def unlink(self):
        invalidate_model_cache(self.env, self._name)
        payload = json.dumps({"model": self._name})
        self.env.cr.execute("SELECT pg_notify(%s, %s)", ("distributed_cache_invalidation", payload))
        return super().unlink()

    @api.model
    def rpc_ensure_executable(self, cmd_name):
        try:
            utils = self.env["zero_sudo.security.utils"]
            path = utils._ensure_executable(cmd_name)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @api.model
    def check_heartbeat_rpc(self, hb_uuid, interval_sec):
        check_id = self._get_check_id_by_uuid(hb_uuid)
        if not check_id:
            return False
        check = self.env["pager.check"].browse(check_id)
        if not check.last_heartbeat:
            return False
        delta = (fields.Datetime.now() - check.last_heartbeat).total_seconds()
        return delta <= interval_sec

    @api.model
    def _get_config_path(self):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "daemon")
        )
        return os.path.join(base_dir, "pager_config.yaml")

    def action_pull_from_yaml(self):
        if not yaml:
            raise UserError(_("PyYAML is not installed."))
        path = self._get_config_path()
        if not os.path.exists(path):
            raise UserError(_("No YAML configuration found at %s") % path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise UserError(_("Invalid YAML Format: %s") % str(e))

        self.env["pager.check"].search([], limit=1000).unlink()
        checks = data.get("checks", []) if isinstance(data, dict) else []
        for c in checks:
            self.env["pager.check"].create(
                {
                    "name": c.get("name", "Unnamed"),
                    "check_type": c.get("type", "system"),
                    "target": c.get("target", ""),
                    "port": c.get("port", 0),
                    "payload_send": c.get("send", ""),
                    "payload_send_hex": c.get("send_hex", ""),
                    "payload_expect": c.get("expect", ""),
                    "dbname": c.get("dbname", ""),
                    "dbuser": c.get("user", ""),
                    "dbpass": c.get("password", ""),
                    "query": c.get("query", ""),
                    "script": c.get("script", ""),
                    "rpc_method": c.get("rpc_method", ""),
                    "rpc_params": c.get("rpc_params", ""),
                    "regex": c.get("regex", ""),
                    "critical_threshold": c.get("critical", 0),
                    "warning_threshold": c.get("warning", 0),
                    "snmp_community": c.get("snmp_community", ""),
                    "snmp_oid": c.get("snmp_oid", ""),
                    "partition": c.get("partition", "/"),
                    "interval": c.get("interval", 60),
                    "grace_period": c.get("grace", 0),
                    "auto_remediate_script": c.get("remediate", ""),
                }
            )

        all_checks = self.env["pager.check"].search([], limit=1000)
        name_to_id = {rec.name: rec.id for rec in all_checks}
        for c in checks:
            if (
                c.get("parent")
                and c.get("parent") in name_to_id
                and c.get("name") in name_to_id
            ):
                check_rec = next(
                    (r for r in all_checks if r.id == name_to_id[c.get("name")]), None
                )
                if check_rec:
                    check_rec.write({"parent_check_id": name_to_id[c.get("parent")]})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Successful"),
                "message": _("Database checks updated from YAML file."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_push_to_yaml(self):
        # [%ANCHOR: generalized_pager_config]
        if not yaml:
            raise UserError(_("PyYAML is not installed."))
        checks = self.env["pager.check"].search([("active", "=", True)], limit=1000)
        check_list = []
        for c in checks:
            d = {
                "name": c.name,
                "type": c.check_type,
                "target": c.target,
                "interval": c.interval,
            }
            if c.port: d["port"] = c.port
            if c.payload_send: d["send"] = c.payload_send
            if c.payload_send_hex: d["send_hex"] = c.payload_send_hex
            if c.payload_expect: d["expect"] = c.payload_expect
            if c.dbname: d["dbname"] = c.dbname
            if c.dbuser: d["user"] = c.dbuser
            if c.dbpass: d["password"] = c.dbpass
            if c.query: d["query"] = c.query
            if c.script: d["script"] = c.script
            if c.rpc_method: d["rpc_method"] = c.rpc_method
            if c.rpc_params: d["rpc_params"] = c.rpc_params
            if c.regex: d["regex"] = c.regex
            if c.critical_threshold: d["critical"] = c.critical_threshold
            if c.warning_threshold: d["warning"] = c.warning_threshold
            if c.snmp_community: d["snmp_community"] = c.snmp_community
            if c.snmp_oid: d["snmp_oid"] = c.snmp_oid
            if c.partition and c.partition != "/": d["partition"] = c.partition
            if c.grace_period: d["grace"] = c.grace_period
            if c.parent_check_id: d["parent"] = c.parent_check_id.name
            if c.maintenance_start: d["maint_start"] = c.maintenance_start.strftime("%Y-%m-%d %H:%M:%S")
            if c.maintenance_end: d["maint_end"] = c.maintenance_end.strftime("%Y-%m-%d %H:%M:%S")
            if c.auto_remediate_script: d["remediate"] = c.auto_remediate_script
            if c.check_type == "heartbeat": d["uuid"] = c.heartbeat_uuid
            check_list.append(d)

        yaml_content = yaml.safe_dump({"checks": check_list}, sort_keys=False)
        path = self._get_config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Export Successful"),
                "message": _("Checks exported to YAML daemon configuration."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_trigger_check(self):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Daemon Notified"),
                "message": _(
                    "The external SRE daemon operates asynchronously outside of Odoo. It will execute this check on its next polling cycle."
                ),
                "type": "info",
                "sticky": False,
            },
        }

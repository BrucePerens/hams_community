import uuid
from odoo import models, fields, api, _, tools


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
        ],
        string="Monitor Type",
        required=True,
    )

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
    @tools.ormcache("hb_uuid")
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

    def unlink(self):
        self.env.registry.clear_cache()
        return super().unlink()

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

import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import yaml
except ImportError:
    yaml = None


class PagerConfigWizard(models.TransientModel):
    _name = "pager.config.wizard"
    _description = "Pager Configuration Wizard"

    yaml_content = fields.Text(
        string="YAML Configuration", default=lambda self: self._default_yaml()
    )

    def _get_config_path(self):
        # Securely resolve the absolute path to the daemon's configuration file in the repository
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "daemons", "pager_duty")
        )
        return os.path.join(base_dir, "pager_config.yaml")

    @api.model
    def _default_yaml(self):
        path = self._get_config_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "# No configuration file found at %s" % path

    def action_load_from_file(self):
        """Reads the physical YAML file from the filesystem into the wizard."""
        self.yaml_content = self._default_yaml()
        return {
            "type": "ir.actions.act_window",
            "res_model": "pager.config.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_generate_yaml(self):
        """Reads the database records and generates a fresh YAML representation."""
        if not yaml:
            raise UserError(
                _("PyYAML is not installed. Please run pip install PyYAML.")
            )

        checks = self.env["pager.check"].search([("active", "=", True)], limit=1000)
        check_list = []
        for c in checks:
            d = {
                "name": c.name,
                "type": c.check_type,
                "target": c.target,
                "interval": c.interval,
            }
            if c.port:
                d["port"] = c.port
            if c.payload_send:
                d["send"] = c.payload_send
            if c.payload_send_hex:
                d["send_hex"] = c.payload_send_hex
            if c.payload_expect:
                d["expect"] = c.payload_expect
            if c.dbname:
                d["dbname"] = c.dbname
            if c.dbuser:
                d["user"] = c.dbuser
            if c.dbpass:
                d["password"] = c.dbpass
            if c.query:
                d["query"] = c.query
            if c.script:
                d["script"] = c.script
            if c.rpc_method:
                d["rpc_method"] = c.rpc_method
            if c.rpc_params:
                d["rpc_params"] = c.rpc_params
            if c.regex:
                d["regex"] = c.regex
            if c.critical_threshold:
                d["critical"] = c.critical_threshold
            if c.warning_threshold:
                d["warning"] = c.warning_threshold
            if c.snmp_community:
                d["snmp_community"] = c.snmp_community
            if c.snmp_oid:
                d["snmp_oid"] = c.snmp_oid
            if c.partition:
                d["partition"] = c.partition
            if c.grace_period:
                d["grace"] = c.grace_period
            if c.parent_check_id:
                d["parent"] = c.parent_check_id.name
            if c.maintenance_start:
                d["maint_start"] = c.maintenance_start.strftime("%Y-%m-%d %H:%M:%S")
            if c.maintenance_end:
                d["maint_end"] = c.maintenance_end.strftime("%Y-%m-%d %H:%M:%S")
            if c.auto_remediate_script:
                d["remediate"] = c.auto_remediate_script
            if c.check_type == "heartbeat":
                d["uuid"] = c.heartbeat_uuid
            check_list.append(d)

        self.yaml_content = yaml.safe_dump({"checks": check_list}, sort_keys=False)
        return {
            "type": "ir.actions.act_window",
            "res_model": "pager.config.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_save_to_file_and_db(self):
        """Parses the YAML, updates the DB graphically, and physically writes the daemon config file."""
        # [%ANCHOR: generalized_pager_config]
        if not yaml:
            raise UserError(_("PyYAML is not installed."))

        try:
            data = yaml.safe_load(self.yaml_content)
        except Exception as e:
            raise UserError(_("Invalid YAML Format: %s") % str(e))

        # 1. Update Graphical DB State
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

        # Link parents in a second pass to avoid creation order issues
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

        # 2. Write Physical File for Daemon
        path = self._get_config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.yaml_content)

        return {"type": "ir.actions.client", "tag": "reload"}

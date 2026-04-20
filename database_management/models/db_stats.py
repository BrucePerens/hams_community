# -*- coding: utf-8 -*-
import logging
import os
import shutil
import subprocess

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

class DatabaseTableStat(models.Model):
    _name = "database.table.stat"
    _description = "Database Table Statistics (Bloat & Vacuum)"
    _auto = False
    _order = "dead_percent desc"

    table_name = fields.Char(string="Table Name", readonly=True)
    live_tuples = fields.Integer(string="Live Tuples", readonly=True)
    dead_tuples = fields.Integer(string="Dead Tuples", readonly=True)
    dead_percent = fields.Float(string="Dead % (Bloat)", readonly=True)
    total_size_mb = fields.Float(string="Total Size (MB)", readonly=True)
    cache_hit_percent = fields.Float(
        string="Cache Hit %",
        readonly=True,
        help="Percentage of data reads satisfied by RAM rather than Disk I/O.",
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW database_table_stat AS (
                SELECT
                    row_number() OVER () as id,
                    t.relname as table_name,
                    t.n_live_tup as live_tuples,
                    t.n_dead_tup as dead_tuples,
                    CASE WHEN t.n_live_tup + t.n_dead_tup > 0 THEN (t.n_dead_tup::float / (t.n_live_tup + t.n_dead_tup)) * 100 ELSE 0 END as dead_percent,
                    pg_total_relation_size(t.relid) / (1024.0 * 1024.0) as total_size_mb,
                    CASE WHEN i.heap_blks_read + i.heap_blks_hit > 0 THEN (i.heap_blks_hit::float / (i.heap_blks_hit + i.heap_blks_read)) * 100 ELSE 0 END as cache_hit_percent
                FROM pg_stat_user_tables t
                JOIN pg_statio_user_tables i ON t.relid = i.relid
            )
        """)

    def _register_hook(self):
        # [@ANCHOR: db_doc_injection]
        # Tests [@ANCHOR: db_doc_injection]
        """
        Wait until all modules are loaded, then install documentation if
        manual_library or knowledge is present.
        """
        super()._register_hook()
        # Only run if we are in a proper request or registry loading context
        # to avoid duplicate work during transient registry states.
        if not self.env.context.get("install_mode") and not self.env.context.get("module_uninstall"):
             self._install_knowledge_docs(self.env)

    @api.model
    def _install_knowledge_docs(self, env):
        """
        Checks if the knowledge.article API is present in the environment.
        If it is, reads the standalone HTML documentation file and installs it.
        """
        if "knowledge.article" not in env:
            return

        # Use the specialized service account for Database Management
        svc_uid = env["zero_sudo.security.utils"]._get_service_uid(
            "database_management.user_database_management_service"
        )
        if not svc_uid:
            return

        # Dynamically add to manual_library group if present (soft dependency)
        manual_group = env.ref(
            "manual_library.group_manual_library_service_account",
            raise_if_not_found=False,
        )
        if manual_group:
            user = env["res.users"].browse(svc_uid)
            if manual_group not in user.group_ids:
                facility_uid = env["zero_sudo.security.utils"]._get_service_uid(
                    "zero_sudo.odoo_facility_service_internal"
                )
                user.with_user(facility_uid).with_context(mail_notrack=True, prefetch_fields=False).write({"group_ids": [(4, manual_group.id)]})

        article_model = (
            env["knowledge.article"]
            .with_user(svc_uid)
            .with_context(mail_notrack=True, prefetch_fields=False)
        )

        existing = article_model.search(
            [("name", "=", "Database Management Guide")], limit=1
        )

        if not existing:
            try:
                with file_open("database_management/data/documentation.html", "r") as f:
                    doc_body = f.read()
            except Exception as e:
                doc_body = f"<h1>Database Management Guide</h1><p>Welcome to the Database Management module.</p><p>Error loading documentation file: {e}</p>"

            vals = {
                "name": "Database Management Guide",
                "body": doc_body,
            }
            if "is_published" in article_model._fields:
                vals["is_published"] = True
            if "internal_permission" in article_model._fields:
                vals["internal_permission"] = "read"
            if "icon" in article_model._fields:
                vals["icon"] = "🛢"

            article_model.create(vals)

    def _get_executable(self, cmd_name):
        path = shutil.which(cmd_name)
        if path:
            return path

        pkg_map = {"vacuumdb": "postgresql-client"}
        if cmd_name == "vacuumdb" and "binary.manifest" in self.env:
            svc_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
                "database_management.user_database_management_service"
            )
            return (
                self.env["binary.manifest"]
                .with_user(svc_uid)
                .ensure_executable("vacuumdb")
            )

        pkg = pkg_map.get(cmd_name, cmd_name)
        raise UserError(
            _(
                "Missing dependency: '%s'. Please install via OS package manager (e.g., 'apt-get install %s')."
            )
            % (cmd_name, pkg)
        )

    def action_vacuum_analyze(self):
        # [@ANCHOR: vacuum_analyze]
        # Tests [@ANCHOR: vacuum_analyze]
        exe = self._get_executable("vacuumdb")
        db_name = self.env.cr.dbname
        env_vars = os.environ.copy()

        for rec in self:
            try:
                # The subprocess bypasses the active ORM transaction block allowing physical vacuuming
                res = subprocess.run(
                    [exe, "-z", "-t", rec.table_name, db_name],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env_vars,
                    shell=False,
                )
                if res.returncode != 0:
                    raise UserError(
                        _("Vacuum failed for %s: %s") % (rec.table_name, res.stderr)
                    )
            except subprocess.TimeoutExpired:
                raise UserError(_("Vacuum timed out for %s.") % rec.table_name)
            except Exception as e:
                raise UserError(_("Error executing vacuumdb: %s") % str(e))
        return True

    @api.model
    def cron_check_bloat(self):
        # [@ANCHOR: bloat_alert_synergy]
        # Tests [@ANCHOR: bloat_alert_synergy]
        high_bloat = self.env["database.table.stat"].search(
            [("dead_percent", ">", 20.0), ("dead_tuples", ">", 10000)], limit=1000
        )
        if high_bloat and "pager.incident" in self.env:
            try:
                pager_uid = self.env["zero_sudo.security.utils"]._get_service_uid(
                    "pager_duty.user_pager_service_internal"
                )
                tables = ", ".join(
                    [f"{t.table_name} ({t.dead_percent:.1f}%%)" for t in high_bloat]
                )
                self.env["pager.incident"].with_user(pager_uid).report_incident(
                    {
                        "source": "DBA Autovacuum Monitor",
                        "severity": "medium",
                        "description": f"Database Bloat Warning! The following tables have >20%% dead tuples and require a manual Vacuum Analyze: {tables}",
                    }
                )
            except Exception as e:
                _logger.warning("An error occurred: %s", e)


class DatabaseQueryStat(models.Model):
    # [@ANCHOR: db_slow_queries]
    # Tests [@ANCHOR: db_slow_queries]
    _name = "database.query.stat"
    _description = "Slow Query Tracking"
    _auto = False
    _order = "total_time desc"

    query = fields.Text(string="SQL Query", readonly=True)
    calls = fields.Integer(string="Execution Count", readonly=True)
    total_time = fields.Float(string="Total Time (ms)", readonly=True)
    mean_time = fields.Float(string="Mean Time (ms)", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
        )
        if self.env.cr.fetchone():
            self.env.cr.execute("""
                CREATE OR REPLACE VIEW database_query_stat AS (
                    SELECT
                        row_number() OVER () as id,
                        query,
                        calls,
                        total_exec_time as total_time,
                        mean_exec_time as mean_time
                    FROM pg_stat_statements
                )
            """)
        else:
            self.env.cr.execute("""
                CREATE OR REPLACE VIEW database_query_stat AS (
                    SELECT 1 as id, 'pg_stat_statements extension not installed on host.' as query, 0 as calls, 0.0 as total_time, 0.0 as mean_time
                )
            """)


class DatabaseActivity(models.Model):
    # [@ANCHOR: db_active_sessions]
    # Tests [@ANCHOR: db_active_sessions]
    _name = "database.activity"
    _description = "Active Database Sessions"
    _auto = False
    _order = "duration desc"

    pid = fields.Integer(string="PID", readonly=True)
    usename = fields.Char(string="User", readonly=True)
    state = fields.Char(string="State", readonly=True)
    query = fields.Text(string="Active Query", readonly=True)
    duration = fields.Float(string="Duration (s)", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW database_activity AS (
                SELECT
                    pid as id,
                    pid,
                    usename,
                    state,
                    query,
                    EXTRACT(EPOCH FROM (now() - query_start)) as duration
                FROM pg_stat_activity
                WHERE datname = current_database() AND pid <> pg_backend_pid()
            )
        """)

    def action_terminate_backend(self):
        # [@ANCHOR: db_terminate_backend]
        # Tests [@ANCHOR: db_terminate_backend]
        for rec in self:
            # Parameterized execution protects against SQL injection
            self.env.cr.execute("SELECT pg_terminate_backend(%s)", (rec.pid,))
        return True


class DatabaseIndexStat(models.Model):
    # [@ANCHOR: db_index_stats]
    # Tests [@ANCHOR: db_index_stats]
    _name = "database.index.stat"
    _description = "Database Index Health"
    _auto = False
    _order = "idx_scan asc"

    table_name = fields.Char(string="Table Name", readonly=True)
    index_name = fields.Char(string="Index Name", readonly=True)
    idx_scan = fields.Integer(string="Total Scans (Usage)", readonly=True)
    index_size_kb = fields.Float(string="Size (KB)", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW database_index_stat AS (
                SELECT
                    row_number() OVER () as id,
                    relname as table_name,
                    indexrelname as index_name,
                    idx_scan,
                    pg_relation_size(indexrelid) / 1024.0 as index_size_kb
                FROM pg_stat_user_indexes
                JOIN pg_index USING (indexrelid)
                WHERE indisunique IS FALSE
            )
        """)

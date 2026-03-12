# Runbook: Daemon Handoff Specifications (CSP Architecture)

**Context:** This document specifies the architectural requirements for transitioning the remaining synchronous, high-I/O Odoo tasks into isolated, durable RabbitMQ daemons.

To prevent "split-brain" states and ensure Odoo survives WSGI restarts, these daemons must strictly follow the **Asynchronous Bastion Pattern**:
1. Odoo creates a tracking record in PostgreSQL and pushes a payload to RabbitMQ via `env.cr.postcommit.add()`.
2. The daemon consumes the message and executes the heavy operation.
3. The daemon communicates back to Odoo via XML-RPC to update the tracking record's state and logs, allowing the UI to poll the progress.

---

## 1. Backup Orchestration Daemon (`backup_worker`)

**Trigger:** A system administrator clicks "Run Backup Now" in the UI.
**The Problem:** Running `kopia` or `pgbackrest` via `subprocess.run` inside Odoo blocks the WSGI worker for minutes or hours, causing timeouts and memory bloat.

### Implementation Spec
* **Odoo State Model:** Create `ham.backup.job`.
  * Fields: `job_type` (kopia/pgbackrest), `state` (pending, processing, done, failed), `output_log` (Text).
* **Communication:** Odoo pushes `{"job_id": 123, "type": "kopia"}` to the `backup_tasks` RabbitMQ queue.
* **Daemon Execution:** The Python daemon picks up the message and executes the OS-level binary using `subprocess.Popen`.
* **Progress Tracking:** As the subprocess yields lines to `stdout/stderr`, the daemon buffers them and executes an XML-RPC call `execute_kw('ham.backup.job', 'write', [[job_id], {'output_log': buffered_text}])` every few seconds so the Odoo UI can stream the live terminal output to the administrator.

---

## 2. Database Administration Daemon (`dba_worker`)

**Trigger:** An admin triggers a manual `VACUUM ANALYZE` on a massive table like `ham_qso`.
**The Problem:** Executing vacuum commands inside Odoo's standard ORM transaction blocks will trigger `ActiveSqlTransaction` crashes.

### Implementation Spec
* **Odoo State Model:** Create `ham.dba.job`.
  * Fields: `target_table`, `state` (pending, processing, done, failed), `error_log`.
* **Communication:** Odoo pushes `{"job_id": 456, "table": "ham_qso"}` to the `dba_tasks` queue.
* **Daemon Execution:** The daemon connects to PostgreSQL directly using `psycopg2`. Crucially, it must set `connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)` to execute the vacuum safely outside a transaction block.
* **Progress Tracking:** Upon completion or exception, the daemon uses a *separate* XML-RPC connection to Odoo to update the `ham.dba.job` state, which the UI polls.

---

## 3. Cloudflare WAF Sync Daemon (`cloudflare_sync`)

**Trigger:** A malicious bot triggers a hidden honeypot on a public form.
**The Problem:** The current synchronous HTTP call to Cloudflare's API means if Cloudflare is slow or offline, the Odoo worker hangs, compounding the DoS attack.

### Implementation Spec
* **Odoo State Model:** Create `cloudflare.waf.job`.
  * Fields: `target_ip`, `action` (ban/unban), `state` (pending, done, failed).
* **Communication:** Odoo pushes the IP to the `cloudflare_tasks` queue.
* **Daemon Execution:** The daemon hits the Cloudflare REST API. If Cloudflare returns a 5xx error or rate-limits the daemon, the daemon `nack`s the message in RabbitMQ to retry it later using exponential backoff.
* **Progress Tracking:** Once Cloudflare returns a 200 OK, the daemon ACKs the message and updates the Odoo tracking record to `done`.

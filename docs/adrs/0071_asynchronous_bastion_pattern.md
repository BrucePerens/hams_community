# ADR 0071: Asynchronous Bastion Pattern for External I/O

## Status
Accepted

## Context
Odoo's architecture relies on single-threaded WSGI web workers that block during execution. If a web worker attempts to perform heavy file parsing, connect to an external REST API (like Cloudflare or PowerDNS), or execute an OS-level binary (like `kopia` or `vacuumdb`), it risks hanging indefinitely. If the external network drops, the worker hits a timeout, the transaction rolls back, and the user receives a 500 Internal Server Error.

While offloading tasks to RabbitMQ solves the blocking issue, a simple "fire-and-forget" queue leaves the Odoo UI completely blind to the task's ultimate success or failure. If a daemon fails to process a task, the user assumes it succeeded because the initial web request returned a 200 OK.

## Decision
We mandate the **Asynchronous Bastion Pattern** for all external daemons interacting with the platform. This guarantees robust transaction boundaries, prevents split-brain states across restarts, and provides immediate UI feedback.

The pattern consists of four strict steps:
1. **State Initialization:** The Odoo controller or ORM method creates a tracking record (e.g., `custom.dns.zone` or `custom.task.queue`) and sets its status field to `pending`.
2. **Transactional Dispatch:** Odoo uses `env.cr.postcommit.add()` to push the task payload to RabbitMQ. This ensures the daemon is *only* notified if the database transaction successfully commits.
3. **Isolated Execution:** The standalone Python daemon consumes the message and executes the dangerous/heavy I/O operation in its own protected memory space.
4. **XML-RPC Callback:** Upon completion or failure, the daemon executes an XML-RPC call back to Odoo (e.g., `action_callback(status, log)`). This updates the tracking record's state to `done` or `failed` and populates an error log, allowing the frontend UI to display the exact status.

## Consequences
* **Resiliency:** Odoo workers never block on external APIs or disk I/O.
* **Visibility:** Administrators and users can view exact error traces from external daemons directly inside the Odoo form views.
* **Fault Tolerance:** If Odoo restarts or crashes, the RabbitMQ messages remain durable. The daemon will continue processing and successfully report the status back to Odoo once it is back online.

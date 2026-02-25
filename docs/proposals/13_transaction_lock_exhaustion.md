# Proposal 13: Transaction Lifecycle & Lock Exhaustion Remediation

## 1. Architectural Context
We successfully implemented bounded chunking and `time.sleep()` rate-limiting in our background workers (ADR-0022). However, in the `_async_gdpr_erasure` background thread and the `process_queue` Cloudflare Cron, the `env.cr.commit()` statement is positioned *outside* the `while True` loop (or entirely omitted, relying on Odoo's implicit cron commit).

Because PostgreSQL locks rows and tables during an active transaction, sleeping *while the transaction is still open* holds those locks hostage, blocking other WSGI workers and severely degrading platform performance.

## 2. Integration Design

### A. Micro-Transaction Refactoring
**Targets:** `user_websites/controllers/main.py`, `cloudflare/models/purge_queue.py`, `ham_logbook/models/res_users.py`, `ham_testing/models/res_users.py`
* **The Fix:** The `env.cr.commit()` call MUST be moved *inside* the `while True` loop, immediately executing before the `time.sleep()` call.
* **Mechanics:** By committing inside the loop, the background worker fully releases its PostgreSQL locks. It then sleeps (allowing other web workers to use the database pool), and initiates a fresh transaction on the next iteration of the loop.

## 3. BDD Acceptance Criteria
* **Story:** As a database administrator, I want background tasks to release their DB locks while sleeping, so standard user traffic is not blocked.
    * *Given* a background thread executing a 50,000 record GDPR erasure
    * *When* the chunk limit (5000) is reached
    * *Then* the script MUST explicitly call `env.cr.commit()` BEFORE calling `time.sleep()`.

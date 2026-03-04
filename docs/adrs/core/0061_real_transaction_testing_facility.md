# ADR 0061: Real Transaction Testing Facility

## Status
Accepted

## Context
Odoo's default testing class (`TransactionCase`) wraps test execution in an uncommitted PostgreSQL `SAVEPOINT`. This ensures tests execute rapidly and automatically rollback, preventing database pollution. However, this artificial environment fundamentally breaks the ORM's local memory cache for inverse relational fields (e.g., `One2many` mappings). Because the transaction never commits, the ORM frequently evaluates these fields as empty, leading to false negatives in tests. Furthermore, it prevents accurate testing of cross-worker cache invalidation (Redis pub/sub) and background daemons that require committed data to operate.

## Decision
We have introduced a standalone open-source testing module: `test_real_transaction`. It provides the `RealTransactionCase` class, which bypasses the Odoo test cursor wrapper entirely and provides a real, committable PostgreSQL database connection.

To prevent database pollution, this facility automatically instruments Odoo's `BaseModel.create()` to track generated records and forcefully unlinks them during `tearDown()`. It also employs a strict SQL Leak Detector that snapshots the entire database schema's row counts before and after the test, instantly failing the build if un-tracked data escapes into the persistent database.

## Consequences
Because `RealTransactionCase` incurs a massive performance penalty (10x to 50x slower per test) due to physical disk I/O (`fsync`), ORM teardown overhead, and full-schema table scans, it **MUST NOT** be used as the default testing class.

* **The 95% Rule:** Developers MUST use standard `TransactionCase` for standard business logic, access rights, UI tours, constraints, and computations.
* **The Surgical Tool (5%):** `RealTransactionCase` is strictly reserved for edge-cases that cross the transaction boundary, such as:
  * Evaluating complex `One2many` Method Resolution Order (MRO) boundary anomalies.
  * Testing Redis pub/sub cache invalidation across workers.
  * Testing background daemons that spawn their own database cursors.
  * Testing explicit PostgreSQL locks (`pg_advisory_xact_lock`).

## Human Time vs. Machine Time (The Exhaustive Testing Philosophy)
Machine computing time is virtually free, whereas human developer time is incredibly expensive. While the `RealTransactionCase` must be used sparingly to prevent the CI/CD pipeline from grinding to a halt, this restriction does **not** mean we should write fewer tests.

On the contrary, developers MUST aggressively write exhaustive, comprehensive automated tests using the standard, lightning-fast `TransactionCase`. By offloading the diagnostic burden to the machine, we save a tremendous amount of human time that would otherwise be wasted manually clicking through the user interface, attempting to replicate edge cases, or parsing server logs. If a machine can test it in a millisecond, a human should never have to test it manually.

# ADR 0061: Real Transaction Testing Facility

## Context
Testing Werkzeug HTTP controllers, Redis pub/sub daemons, and cross-thread transaction boundaries is difficult in standard testing environments because the default cases wrap tests in uncommitted SQL transactions. This causes external worker threads to see empty tables.

## Decision
We utilize real transaction testing methodologies (explicitly committing test data to the database disk) to make data visible to external threads and daemons, ensuring true end-to-end reliability.

## Consequences
Real transaction testing incurs a performance penalty due to physical disk I/O, ORM teardown overhead, and full-schema table scans. However, architectural realism takes precedence over minor execution speed optimizations.

* **The Anti-Mocking Mandate:** Real transaction testing MUST be used in favor of mocking. You are strictly forbidden from mocking core objects simply to bypass Werkzeug cross-thread cursor isolation.
* **The Performance Threshold:** If a full test run of a repository is not going to be an entire minute slower from the incorporation of real transactions, its use is permitted in general.
* **Primary Use Cases:** It is the required standard for edge-cases that cross the transaction boundary, such as:
  * Testing HTTP Controllers and JSON-RPC API routes via Werkzeug.
  * Evaluating complex Method Resolution Order boundary anomalies.
  * Testing Redis pub/sub cache invalidation across workers.
  * Testing background daemons that spawn their own database cursors.
  * Testing explicit PostgreSQL locks.

# ADR 0051: Architectural Behavior & Resilience Testing Mandates

## Status
Accepted

## Context
The platform utilizes strict architectural boundaries that are not inherently security-related but are vital for system resilience and performance. This includes Graceful Degradation for Soft Dependencies (ADR-0014, ADR-0021), Event Bus Payload Routing (ADR-0012, ADR-0027), and Zero-DB Execution (ADR-0003). Relying on manual developer review to ensure these behaviors persist across refactors is error-prone and risks catastrophic platform failure (e.g., crashing the deployment if an optional app is missing, or locking the database if the DX cluster accidentally executes disk writes).

## Decision
We mandate that all architectural resilience behaviors MUST be explicitly verified via automated unit testing:

### 1. Graceful Degradation (Soft Dependencies)
Any module interacting with a Soft Dependency MUST include a unit test that explicitly strips or mocks the absence of the target model from the environment registry. The test MUST assert that the execution returns cleanly or falls back to default behavior without raising a `KeyError`, `AttributeError`, or crashing the transaction.

### 2. Event Bus & CQRS Payload Generation
Any ORM method designated to trigger an external queue (RabbitMQ, Postgres `NOTIFY`, or external cache invalidation) MUST include a test asserting that the payload is formatted correctly and pushed to the internal bus during the transaction. This ensures that background daemons will not silently starve due to upstream ORM refactoring.

### 3. Zero-DB Execution Verification
Any model designated as a Zero-DB `AbstractModel` (e.g., `ham.dx.spot`) MUST include a unit test utilizing `self.assertQueryCount()` specifically targeting write operations. The test MUST mathematically prove that pushing data through the model executes exactly 0 disk-write queries (`INSERT` or `UPDATE`), preventing accidental I/O exhaustion regressions.

## Consequences
* **Positive:** Mathematically protects the platform's high-throughput architecture. Refactoring a Zero-DB route or an event hook will immediately fail CI/CD if it introduces synchronous disk locks or drops payloads.
* **Negative:** Requires advanced testing techniques, including robust environment mocking and strict query-counter isolation, increasing the complexity of the test suites.

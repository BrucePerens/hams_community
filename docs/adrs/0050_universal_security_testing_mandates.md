# ADR 0050: Universal Security & Compliance Testing Mandates

## Status
Accepted

## Context
While ADRs define the operational rules for Proxy Ownership (ADR-0008), GDPR Data Erasure (ADR-0009 & ADR-0020), and API Idempotency (ADR-0011), relying purely on developer discipline during implementation is insufficient. To mathematically guarantee that these critical security and compliance boundaries are never breached by regressions, we must bind them to strict automated testing patterns.

## Decision
The following behaviors MUST be explicitly proven via unit tests in any module that implements them:

### 1. Proxy Ownership IDOR (The Three-Persona Mandate)
Any model inheriting `user_websites.owned.mixin` MUST include an Access Control test suite covering the three core personas defined in the platform's Definition of Done:
* **Owner:** Assert that the assigned proxy owner (`owner_user_id`) can successfully create, edit, and delete the record.
* **User:** Assert that an unrelated authenticated user receives a hard `AccessError` (IDOR block) when attempting to write to or delete the target record.
* **Guest:** Assert that an unauthenticated public user is strictly blocked from mutations.

### 2. GDPR Erasure & Anonymization Proof
Any module that extends the `res.users._execute_gdpr_erasure()` hook MUST include a unit test that physically simulates account destruction. The test MUST:
1. Create dummy data linked to the target user.
2. Execute `user._execute_gdpr_erasure()`.
3. Explicitly query the database to assert that the data was either completely destroyed (via `.sudo().unlink()`) or properly anonymized (via `ondelete='set null'`) per the module's legal requirements.

### 3. API Idempotency Zero-Query Proof
Any high-velocity API endpoint requiring an `X-Idempotency-Key` MUST include a test simulating a network retry. The test MUST:
1. Submit a valid POST request with the idempotency key and verify the database mutation.
2. Resubmit the exact same request wrapped in `with self.assertQueryCount(0):`.
3. Assert that the second request returns the successful cached payload without hitting the PostgreSQL database.

## Consequences
* **Positive:** Absolutely guarantees that IDOR vulnerabilities, ghost records, and duplicate API ingestions are mathematically impossible to deploy.
* **Negative:** Increases the boilerplate required to merge new features, as developers must meticulously mock HTTP requests, cache states, and user sessions across three distinct privilege boundaries.

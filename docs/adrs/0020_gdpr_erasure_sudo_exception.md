# ADR 0017: GDPR Erasure `.sudo()` Exception

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
The Zero-Sudo policy dictates using a Service Account for elevated privileges. However, when executing a GDPR Right to Erasure request, the system must cascade and hard-delete all user data across multiple models. If dependent models or cascaded data are not explicitly owned by the Service Account (or if record rules restrict the Service Account), the `unlink()` operation will fail. This leaves orphaned data and violates regulatory compliance (GDPR/CCPA).

## Decision
We explicitly authorize the use of the `.sudo().unlink()` method exclusively within the `_execute_gdpr_erasure()` hook. The linter's Burn List prohibition of `.sudo()` will be bypassed in this specific context using the `# burn-ignore` directive.

## Consequences
* **Positive:** Guarantees complete data destruction across all models, ensuring strict GDPR compliance and preventing ghost records.
* **Negative:** Creates a localized exception to the Zero-Sudo architecture, requiring strict code review to ensure it is only used for data destruction.

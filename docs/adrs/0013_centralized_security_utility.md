# ADR 0013: Centralized Security Utility & Sudo Abstraction

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
Under the Zero-Sudo mandate, developers cannot use `.sudo()` inline. However, standard operations—such as resolving a Service Account's XML ID (`ir.model.data`) or fetching a system configuration parameter (`ir.config_parameter`)—natively require escalated privileges. If every developer writes their own workaround, it creates fragmented security boundaries and potential Server-Side Template Injection (SSTI) risks.

## Decision
All escalations required to fetch system data MUST be routed through a centralized utility AbstractModel.
1. **Service Account Lookups:** Developers must use a utility like `_get_service_uid('module.xml_id')`. This method uses `@tools.ormcache` to perform the database lookup exactly once per boot cycle, vastly improving performance.
2. **Parameter Fetching:** Developers must use a centralized wrapper. This method checks requested keys against a strict, hardcoded Python `frozenset` whitelist. Cryptographic keys (like `database.secret`) are explicitly excluded from this whitelist to prevent QWeb injection attacks.

## Consequences
* **Positive:** Centralizes all privilege escalations into a single, highly auditable location. Prevents arbitrary parameter extraction.
* **Negative:** Requires developers to manually update the whitelist whenever a new, benign system parameter is introduced.

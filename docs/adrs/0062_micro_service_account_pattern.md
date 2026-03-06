# ADR 0062: Micro-Service Account Pattern & Separation of Privilege

## Status
Accepted

## Context
The initial Zero-Sudo architecture (ADR-0002) successfully eliminated the dangerous `.sudo()` method by substituting domain-specific Service Accounts (e.g., `api_service_account`, `external_sync_account`). However, over time, these domain accounts became monolithic, accumulating disparate permissions across the ecosystem. For example, a single service was granted rights to send emails, evaluate external registries, and modify users.

Furthermore, developers and AI agents occasionally fell back to using `base.user_admin` to perform cross-domain or framework-level tasks (like writing to `ir.config_parameter`), violating the principle of least privilege and creating massive blast radiuses if a daemon was compromised.

## Decision
We mandate the **Micro-Service Account Pattern** (a strict enforcement of Separation of Privilege). Privilege escalation MUST be separated into hyper-specific proxy accounts dedicated to a single operational flow.

* `mail_service_internal`: Exclusively for dispatching communications and chatter posts.
* `gdpr_service_internal`: Exclusively for cascading hard-deletes and anonymization.
* `config_service_internal`: Exclusively for writing system parameters.
* `reporting_service_internal`: Exclusively for generating analytical reports.

## Consequences
* `base.user_admin` is strictly forbidden from being used as a programmatic proxy for background operations or guest actions.
* If an operation requires elevated rights to cross a domain boundary, a dedicated micro-service account must be provisioned and granted exactly the minimal Record Rules needed for that specific action.

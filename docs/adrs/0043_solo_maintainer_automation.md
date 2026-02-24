# ADR 0043: Hyper-Automation & Solo-Maintainer Optimization

## Status
Accepted

## Context
The Hams.com platform is currently maintained and administered by a single developer. Relying on complex manual deployment steps, repetitive administrative tasks, or extensive memorization of operational procedures creates an unsustainable cognitive load. To allow the platform to scale without forcing the immediate hiring of operational staff, the architecture must actively conserve administrator time and focus.

## Decision
The platform MUST be engineered with extreme automation and streamlined human-in-the-loop interfaces.

1. **Zero-Touch CI/CD & Testing:** All testing, linting (e.g., the Burn List), and deployment steps MUST be fully automated via scripts and CI/CD pipelines (e.g., GitHub Actions, automated Docker Compose builds). The maintainer should not need to memorize or string together complex CLI commands.
2. **Self-Healing over Alerting:** Where possible, the system MUST implement automated reconciliation (e.g., the DNS CQRS loop defined in ADR-0034) rather than paging the administrator to manually fix state drift.
3. **Streamlined Moderation Queues:** When human intervention is absolutely required (e.g., manual license verification or resolving SWL familial collisions), the workflow MUST be centralized into unified, one-click Odoo dashboards. The system MUST pre-fetch and display all necessary context so the administrator does not have to manually cross-reference databases.
4. **Strict Context Preservation:** The Semantic Anchor architecture (ADR-0004) and isolated Task Workspaces (ADR-0016) MUST be rigorously maintained so that the solo developer (or an assisting AI) can instantly regain context on an old feature without relying on human memory.

## Consequences
* **Positive:** Conserves developer energy, prevents burnout, ensures highly consistent deployments, and drastically lowers the operational overhead of running a global platform.
* **Negative:** Requires a higher upfront investment of time to write robust automation scripts, CI/CD pipelines, and intuitive moderation views before a feature can be considered "Done".

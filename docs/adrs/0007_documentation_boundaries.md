# ADR 0007: Documentation Boundaries (Runbooks vs. Deployment Guides)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
As the system infrastructure grew, documentation redundancy occurred between the `docs/runbooks/` directory and the `deploy/` directory. Both began accumulating step-by-step Command Line Interface (CLI) execution steps. This violates the Single Source of Truth principle and creates "synchronization drift," where a command might be updated in a deployment guide but forgotten in a runbook, leading to broken administrative procedures.

## Decision
We are enforcing a strict separation of concerns for system documentation based on Tactical vs. Strategic operational scope:

1. **Tactical Execution (`deploy/`):** 
   Documents in this directory (e.g., `DOCKER_DEPLOYMENT.md`, `DEBIAN_DEPLOYMENT.md`) are the **exclusive** home for step-by-step, copy-paste execution instructions, CLI commands, and exact file paths required to stand up or modify the physical infrastructure.
2. **Strategic Operations (`docs/runbooks/`):**
   Documents here act as high-level Standard Operating Procedures (SOPs). They explain *how* the architecture fits together, what background daemons are responsible for, and how disaster recovery flows operate. **Runbooks MUST NOT contain step-by-step CLI execution commands.** When execution is required, the runbook must provide a hyperlink directing the administrator to the appropriate file in the `deploy/` directory.

## Consequences
* **Positive:** Eliminates synchronization drift. Ensures a Single Source of Truth for critical commands. Makes runbooks cleaner and easier to read for architectural understanding.
* **Negative:** Requires strict discipline from developers and AI agents to refrain from providing "helpful" command-line snippets inside operational runbooks.

# MASTER 11: Agile Development & Documentation Workflow

## Status
Accepted (Consolidates ADRs 0004, 0007, 0016, 0043, 0055, 0056)

## Context & Philosophy
Maintaining architectural cohesion across a large platform relies on strict documentation traceability and minimizing developer (and AI) cognitive load. Documentation must remain perfectly synchronized with source code.

## Decisions & Mandates

### 1. Semantic Anchor Traceability (0004, 0055)
* Source code and Agile documentation (Stories, Runbooks) MUST be mathematically linked using Semantic Anchors (`[%ANCHOR: example_feature_name]`).
* *** **Inline Documentation Placement:** Within module-specific documentation files (like `docs/modules/*.md` or `LLM_DOCUMENTATION.md`), anchors MUST be placed directly inline/adjacent to the specific text, step, or requirement describing the functionality. They must NOT be collected in a disconnected list or standalone chapter at the end of the document. A dedicated `ANCHOR_MANIFEST.md` file is strictly forbidden.
* *** **ADR Exclusion:** Semantic anchors MUST NOT be placed in Architecture Decision Records (ADRs). If an implementation detail needs anchoring, it must be documented in the specific module's documentation..
* When an event crosses an architectural boundary (e.g., Odoo triggers a background daemon), bidirectional anchors MUST bridge the producer and consumer.
* The CI/CD pipeline scans for orphaned or missing anchors and fails the build if the mapping breaks.
### 2. LLM Context Management (See MASTER 14)
* To prevent instruction drift and cognitive overload, LLM interactions MUST strictly adhere to the Context Management mandates outlined in MASTER 14.
* This includes utilizing Isolated Task Workspaces (`tools/create_task_workspace.py`), targeting API contracts over raw implementations, and enforcing the Patch Protocol to minimize output token generation.

### 3. Clear, Conversational Writing Style (0056)
* "Oblique" AI tones, passive voice, and dense corporate jargon are strictly forbidden. All documentation MUST be written conversationally, directly, and plainly.

### ### 4. Documentation Boundaries (0007)
### * `docs/runbooks/` holds strategic Standard Operating Procedures. It MUST NOT contain step-by-step CLI commands.
### * `deploy/` holds tactical deployment steps and CLI commands. Runbooks link here to prevent synchronization drift.
### * **LLM Documentation & API Contracts:** Any technical documentation intended for LLMs (`LLM_DOCUMENTATION.md` or `docs/modules/`) MUST explicitly state the exact Python import paths for any shared classes or utilities to prevent AI agents from hallucinating filenames.

### ### 5. Solo-Maintainer Automation & SRE (0043))
* The platform MUST prioritize self-healing infrastructure (e.g., DNS CQRS loops), zero-touch CI/CD, and highly centralized unified moderation queues to radically compress administrative overhead.
* **JIT Self-Healing Dependencies:** Daemons and modules MUST implement Just-In-Time (JIT) binary resolution. If an expected OS-level package (e.g., `kopia`, `cloudflared`, `etcd`) is missing, the Python code must dynamically download the static standalone executable from official GitHub releases, assign executable permissions, and continue operations without requiring manual human SSH intervention.
* **Automated Disaster Recovery:** The system MUST execute automated Restore Drills to mathematically prove backup integrity rather than relying on assumed success.
* **Auto-Remediation:** SRE monitors MUST support executing local shell scripts to automatically remediate known infrastructure failures (e.g., restarting Docker or rebooting the host via OS-level file flags).

### 6. No Cybercrud Policy (Log Hygiene)
* Repetitive, non-actionable warnings (like missing soft-dependencies or unreachable cache servers during every web request) create "cybercrud" that buries actual critical system issues.
* Warnings that occur inside high-frequency loops, controllers, or `ir.http` routing MUST use a "run-once" global boolean flag per WSGI worker to ensure they print exactly once to the logs and then fall silent.

### 7. Human Time vs. Machine Time (The Time Protection Mandate)
As a solo-maintainer, human developer time is the most expensive and scarce resource. Machine time is virtually free. All architectural decisions MUST aggressively protect the administrator's time by shifting the diagnostic and operational burden to the system:
* **Exhaustive Automated Testing:** Write exhaustive standard tests (using `TransactionCase`) for all CRUD operations, state transitions, and business logic. If a machine can test it in a millisecond, a human should never have to test it manually in the UI.
* **Shift-Left Data Validation:** The cheapest place to fix bad data is before it enters the database. Aggressively validate inputs at the UI and ORM layers. The system MUST instantly reject bad data with clear errors, forcing the user to fix it, rather than silently failing and generating backend logs for the administrator to investigate.
* **Flawless Self-Service & Community Moderation:** Users must be able to recover accounts, change callsigns, and upgrade permissions entirely automatically (e.g., via background FCC database polling). Delegate directory moderation and spam flagging to trusted, verified community members via software-enforced permission tiers.
* **Idempotent Background Jobs:** Never build a scheduled action that requires a human to "resume" it. All cron jobs and daemon workers MUST be completely idempotent, track individual record status, and utilize exponential backoff for failed network calls.
* **Automated Data Pruning (Garbage Collection):** Data MUST have an expiration date unless legally or operationally required. Use background daemons to automatically execute GDPR erasures on dormant unverified accounts and silently clear temporary tracking tables.

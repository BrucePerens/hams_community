# MASTER 04: Modularity & Shared Services

## Status
Accepted (Consolidates ADRs 0014, 0021, 0045, 0046)

## Context & Philosophy
Cross-module dependencies create monolithic entanglement, making the platform brittle and difficult to test. Shared logic and services must be centralized and abstracted to ensure isolated testability and DRY (Don't Repeat Yourself) compliance.

## Decisions & Mandates

### 1. Shared Service Account Centralization
When a Service Account, security group, or foundational utility is used by two or more sibling modules, it MUST be migrated to the `ham_base` module. Higher-level modules reference this shared service securely without creating lateral dependencies.

### 2. Code Deduplication Mandate
Any execution logic (e.g., API authentication, geographic mathematics) duplicated across modules MUST be proactively abstracted into `ham_base` (e.g., `ham.geo.utils`).

### 3. Soft Dependency Injection
Modules MUST utilize Soft Dependencies for non-critical integrations (e.g., Documentation injections via `knowledge.article`).
* Check for the model dynamically: `if 'target.model' in self.env:`.
* Unit tests MUST explicitly verify that execution falls back gracefully if the soft dependency is uninstalled, using `unittest.SkipTest` where appropriate.

### 4. Centralized Reverse Traceability
Any utility or Service Account hosted in `ham_base` MUST include a `CONSUMERS:` block in its docstring.
* This block explicitly lists every active usage across the platform using Semantic Anchors (`[%ANCHOR: example_name]`).
* Developers modifying core utilities MUST consult this block to understand downstream impacts and prevent regression.

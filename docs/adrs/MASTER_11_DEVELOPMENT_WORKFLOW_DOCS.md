# MASTER 11: Agile Development & Documentation Workflow

## Status
Accepted (Consolidates ADRs 0004, 0007, 0016, 0043, 0055, 0056)

## Context & Philosophy
Maintaining architectural cohesion across a large platform relies on strict documentation traceability and minimizing developer (and AI) cognitive load. Documentation must remain perfectly synchronized with source code.

## Decisions & Mandates

### 1. Semantic Anchor Traceability (0004, 0055)
* Source code and Agile documentation (Stories, Runbooks) MUST be mathematically linked using Semantic Anchors (`[%ANCHOR: feature_name]`).
* When an event crosses an architectural boundary (e.g., Odoo triggers a background daemon), bidirectional anchors MUST bridge the producer and consumer.
* The CI/CD pipeline scans for orphaned or missing anchors and fails the build if the mapping breaks.

### 2. LLM Context Management (See MASTER 14)
* To prevent instruction drift and cognitive overload, LLM interactions MUST strictly adhere to the Context Management mandates outlined in MASTER 14.
* This includes utilizing Isolated Task Workspaces (`tools/create_task_workspace.py`), targeting API contracts over raw implementations, and enforcing the Patch Protocol to minimize output token generation.

### 3. Clear, Conversational Writing Style (0056)
* "Oblique" AI tones, passive voice, and dense corporate jargon are strictly forbidden. All documentation MUST be written conversationally, directly, and plainly.

### 4. Documentation Boundaries (0007)
* `docs/runbooks/` holds strategic Standard Operating Procedures. It MUST NOT contain step-by-step CLI commands.
* `deploy/` holds tactical deployment steps and CLI commands. Runbooks link here to prevent synchronization drift.

### 5. Solo-Maintainer Automation (0043)
* The platform MUST prioritize self-healing infrastructure (e.g., DNS CQRS loops), zero-touch CI/CD, and highly centralized unified moderation queues to radically compress administrative overhead.

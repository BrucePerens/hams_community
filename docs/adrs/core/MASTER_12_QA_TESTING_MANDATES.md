# MASTER 12: QA & Automated Testing Mandates

## Status
Accepted (Consolidates ADRs 0044, 0049, 0050, 0051, 0052, 0053, 0054, 0058, 0059, 0061, 0063)

## Context & Philosophy
To guarantee the stability and security of the platform without a massive QA department, all architectural rules and linter bypasses MUST be mathematically proven by exhaustive automated tests before merging.

## Decisions & Mandates

### 1. Fast-Fail Test Pipeline (0044)
* CI/CD and deployment scripts (`START.sh`) MUST execute all static linters and anchor verifiers sequentially and instantly abort on failure before executing time-consuming database rebuilds.

### 2. Linter Bypass Testing & AST Verification (0052, 0058, 0059)
* Using a bypass tag (`# burn-ignore`, `# audit-ignore-*`) to silence the `check_burn_list.py` linter requires an explicit automated test to prove the bypassed logic is safe.
* The bypass comment MUST cross-reference the test anchor.
* The linter performs Deep AST Test Verification (Phase 2). It locates the test file, parses the Abstract Syntax Tree, and verifies that the test function contains the required functional assertions (e.g., `_trigger` for crons, `assertQueryCount` for unbounded searches).
* **Anti-Evasion Mandate:** Tests MUST NOT contain unreachable code (e.g., `return`, `raise`, `break`, `continue` prior to the assertion) or wrap rendering validations (`get_view`, `url_open`) inside `for`/`while` loops. The AST linter will flag these structures as active evasion attempts.

### 3. Bidirectional Test Anchoring (0054)
* Code logic verified by a test MUST include a "Verified by" anchor tag. The test MUST include a "Tests" anchor tag. The CI/CD pipeline enforces this bidirectional mapping.

### 4. XPath Rendering Verification (0053)
* A successful `<xpath>` XML insertion does not guarantee the DOM renders correctly. Tests MUST physically execute `get_view()` or `url_open()` to prove the injected payload actually exists in the compiled architecture.

### 5. Cache Query Counting Mandate (0049)
* Any method utilizing `@tools.ormcache` MUST be tested using `with self.assertQueryCount(0):` to mathematically guarantee zero SQL executions on a cache hit.

### 6. Security & Architecture Behavior Testing (0050, 0051)
* **Proxy Ownership & IDOR (The Multi-Persona Rule):** Tests must rigorously prove data isolation across the entire spectrum of platform users. You MUST assert that the Owner can edit, and that the following distinct personas are violently denied:
  1. Standard Odoo User (No Ham/Web groups)
  2. Web-Only User (Has User Websites group, no Ham groups)
  3. Ham Operator (Fully licensed)
  4. SWL (Prospective Operator)
  5. Public Guest (Unauthenticated)
* **GDPR Erasure:** Tests must assert that calling the erasure hook actually executes the hard-delete cascade.
* **Zero-DB:** Abstract models (e.g., DX Spots) must be tested using `assertQueryCount(0)` on mutations to guarantee they do not write to PostgreSQL.

### 7. The View-Tour UI Mandate
* Every `<template>` and `<record model="ir.ui.view">` defined in XML MUST contain a bidirectional semantic anchor linking it to an automated JS Tour.
* The corresponding `.js` Tour file MUST contain the anchor and MUST explicitly include `trigger:` selectors to prove DOM element validation.
* In cases where a view is purely structural and tested via a Python `HttpCase` (e.g., `url_open` / `get_view`), the `audit-ignore-view` AST bypass may be used.

### 8. Transaction Boundaries & Test Realism (0061)
* The standard `TransactionCase` MUST be used for 95% of tests to maintain pipeline speed.
* The `test_real_transaction.RealTransactionCase` facility MUST be utilized exclusively as a surgical tool for tests requiring physical database commits (e.g., Redis Pub/Sub, external daemons, MRO `One2many` cache anomalies). Its usage incurs a massive performance penalty due to physical disk I/O and leak-detection table scans.

### 9. Human Time vs. Machine Time
* **Exhaustive Coverage Mandate:** Developers MUST write exhaustive standard tests for all CRUD operations, state transitions, and business logic. Machine time is cheap; human time spent manually diagnosing UI bugs is expensive. Offload all possible verification to the automated test suite.

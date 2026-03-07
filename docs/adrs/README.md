# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records (ADRs) that define the structural, security, and operational mandates for the platform.

## Master ADRs (Consolidated Paradigms)

* [MASTER 01: Security & Zero-Sudo Architecture](MASTER_01_SECURITY_ZERO_SUDO.md)
  Enforces the Service Account pattern, web isolation for daemons, and strict limitations on `.sudo()` to prevent privilege escalation.
* [MASTER 03: Edge Routing & Threat Mitigation](MASTER_03_EDGE_ROUTING_THREAT_MITIGATION.md)
  Defines Cloudflare edge orchestration, proactive caching, WAF bot verification, and dynamic Nginx tarpitting via silent honeypots.
* [MASTER 04: Modularity & Shared Services](MASTER_04_MODULARITY_SHARED_SERVICES.md)
  Mandates centralizing shared logic and Service Accounts into the `core_base` module to prevent monolithic cross-module entanglement.
* [MASTER 08: Core Architecture & Performance](MASTER_08_CORE_ARCHITECTURE_PERFORMANCE.md)
  Details the hybrid monolith-daemon structure, distributed Redis caching, asynchronous WSGI offloading, and bounded chunking for O(1) memory mapping.
* [MASTER 10: Core Identity & Access Control](MASTER_10_IDENTITY_ACCESS_CONTROL.md)
  Outlines the Proxy Ownership pattern, domain sandbox mandates (restricting community users from `base.group_user`), and secure admin password management.
* [MASTER 11: Agile Development & Documentation Workflow](MASTER_11_DEVELOPMENT_WORKFLOW_DOCS.md)
  Requires Semantic Anchor traceability, conversational documentation, Just-In-Time (JIT) self-healing dependencies, and a strict "no cybercrud" log policy.
* [MASTER 12: QA & Automated Testing Mandates](MASTER_12_QA_TESTING_MANDATES.md)
  Enforces fast-fail CI/CD pipelines, deep AST test verification for linter bypasses, JS UI tours for all views, and cache query counting.
* [MASTER 14: LLM Context & Cognitive Load Management](MASTER_14_LLM_CONTEXT_MANAGEMENT.md)
  Establishes rules for AI agents, including the use of isolated task workspaces, API contracts over raw implementations, and granular search-and-replace patching.

## Standard ADRs

* [ADR 0060: Strict Syntactic Parsing Mandate](0060_strict_syntactic_parsing_mandate.md)
  Bans the use of regular expressions for parsing structured data (XML, Python, JSON) in favor of proper AST parsers.
* [ADR 0061: Real Transaction Testing Facility](0061_real_transaction_testing_facility.md)
  Introduces the `RealTransactionCase` for tests requiring physical database commits (e.g., background daemons, pub/sub), restricting its use to prevent performance penalties.
* [ADR 0062: Micro-Service Account Pattern](0062_micro_service_account_pattern.md)
  Mandates breaking monolithic service accounts into hyper-specific proxy accounts dedicated to single operational flows.
* [ADR 0063: AST Linter Anti-Evasion Protocols](0063_linter_anti_evasion_protocols.md)
  Upgrades the linter to detect and block "dead code" or "loop" evasions used to bypass CI/CD test verification.
* [ADR 0064: Micro-Service Strict ACL Isolation](0064_micro_service_strict_acl_isolation.md)
  Forbids assigning broad internal ERP groups to Service Accounts just to bypass ORM cascade traps, requiring microscopic explicit ACLs instead.
* [ADR 0065: Headless API Translation Ban](0065_headless_api_translation_ban.md)
  Bans the use of the `_()` translation wrapper around string literals in headless API JSON responses to prevent context crashes.
* [ADR 0066: Secure Cached Resolver Pattern](0066_secure_cached_resolver_pattern.md)
  Requires high-frequency cached lookups to accept an `override_svc_uid` parameter to execute database queries safely under the caller's specific micro-service context.

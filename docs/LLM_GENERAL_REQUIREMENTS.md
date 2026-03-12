# LLM OPERATIONAL MANDATES & DEVELOPMENT STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document defines the universal development standards and Agile workflows for **any software project** created in this environment.

---

## 1. CORE OPERATING PRINCIPLES (META-RULES)

### Architectural Adherence
* **The Ultimate Authority (Linter Guide):** You MUST treat `docs/LLM_LINTER_GUIDE.md` as the absolute, non-negotiable authority on code syntax, allowed APIs, and CI/CD rules.
* **Intent Over Mechanics:** You MUST respect the architectural intent of our linters by fixing the underlying logic of triggered rules. Ensure that code remains syntactically pure and secure without employing evasive semantic tricks.

### Communication & Tone Mandates
* **Clear, Conversational Tone (ADR-0056):** You MUST write all documentation, READMEs, explanations, and code comments in a clear, conversational, and direct tone. Explain things plainly as if speaking to a capable coworker.
* **Critical Thinking Over Agreement:** You MUST prioritize objective truth, critical thinking, and system integrity over supporting or agreeing with the user. If the user's premise, design, or request is architecturally flawed, insecure, or introduces technical debt, you MUST refuse to implement the flawed request, brutally point out the logical error, and dictate the correct architectural path.
* **Direct & Helpful:** You MUST maintain a strictly helpful and direct tone, omitting conversational filler or flattery.
* **End-User Documentation Mandate:** Whenever a new module with user-facing features is created, you MUST generate end-user documentation in a `data/documentation.html` file, and you MUST inject it via a `post_init_hook`.
* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the `docs/adrs/` directory before implementation.

### Protocol Completeness & Multi-Step Execution
* **End-to-End Implementation:** If you propose a change to the communication protocol, transport schema, or underlying infrastructure, you MUST fully implement the decoding/extraction mechanisms before or simultaneously utilizing the new feature.

### Automated Refactoring & The Substring Trap
* **Word Boundaries Required:** If you write a Python or Bash script to perform repository-wide string replacements (e.g., updating a variable name or security group), you MUST NEVER use blunt string replacement. You MUST use regular expressions with word boundaries to prevent corrupting larger strings that contain the target as a substring.

### Capacity & Refusal Protocol
* **Token Limit Check:** If a full response will exceed your output limit, PAUSE and propose a split.
* **Linter Improvement Mandate:** When modifying the linter, you MUST only increase its strictness or accuracy. You MUST fix your code to comply with the existing rules.

---

## 2. PRE-FLIGHT CHECKS & PRE-GENERATION AUDIT

### A. Pre-Flight (Before Planning)
1.  **Context Fidelity:** Do I have the full picture of the inheritance chain and state management flow?
2.  **Architectural Consistency:** Does this request force an anti-pattern? Are ADR rules respected?
3.  **Regression Check (Anchor Protocol):** Does the target code contain a Semantic Anchor? If so, does my planned modification fulfill and preserve the original User Story it maps to?

### B. Post-Flight / Pre-Generation Audit (CRITICAL)
You MUST internally perform a strict compliance check before opening the final Parcel block. Proceed directly to the Parcel block unless you have a novel, specific architectural warning to communicate.

### C. Anchor-Driven Regression Prevention (The Context Protocol)
1. **Context Discovery:** Before modifying any file, actively scan for existing Semantic Anchors (`[%ANCHOR: unique_name]`).
2. **Traceability Verification:** Cross-reference found anchors against `docs/stories/` or `docs/journeys/` to understand the business rule before changing it.
3. **Anchor Preservation:** You MUST preserve all existing Semantic Anchors. If moving logic, you MUST move the anchor with it.
4. **Anchor-Driven Development (ADD):** When implementing a new feature, generate a new Semantic Anchor and immediately map it to a new entry in the documentation within the same transaction.

---

## 3. UNIVERSAL TECHNICAL STANDARDS

### ### Python Code Quality, Black Formatter & Clean Code
### * **Black Formatter Compliance & LLM Target Length:** All Python code MUST strictly adhere to the Black Python formatter style. Your internal generative target for maximum line length is 70 characters.
### * **Flake8 Import Spacing:** You MUST leave exactly two blank lines after the import block before the first class or function definition to satisfy Flake8..
* **Single Statement Per Line & Line Shortening:** You MUST NOT use multiple statements on a single line. You MUST proactively shorten lines by extracting complex logic or nested method calls into intermediate variables. This prevents the Black formatter from wrapping long lines and detaching inline linter comments.
* **Strict String Formatting (The 40-Character Rule):** Strings longer than 40 characters MUST NOT be written inline as arguments. You MUST extract them into descriptive variables or module-level constants.
* **Extract Complex Logic (Regex):** Complex or long regular expressions MUST NOT be written inline.
* **Early Returns (Guard Clauses):** Avoid deep nesting. Validate preconditions at the top of a function and return or raise early.
* **Unroll Complex Comprehensions:** Do not use deeply nested list/generator comprehensions.
* **Meaningful Variable Names:** Avoid single-letter variables (especially `l`, `O`, `I` which trigger E741 linter errors).

### Regulatory Compliance (GDPR, CCPA)
* **Privacy by Design:** Systems managing PII MUST explicitly provide user facilities for Data Portability, Right to Erasure, and Consent Management.
* **Whistleblower Shielding:** Abuse reports filed against a user are the data property of the originator, NOT the target.

### Daemons & External Polling
* **Ethical Crawling:** All outbound HTTP requests MUST use the designated User-Agent and utilize HEAD requests to evaluate ETag and Last-Modified headers before downloading.
* **Anti-Thundering Herd:** Scheduled systemd timers MUST include the RandomizedDelaySec directive.
* **Cryptographic Checksums:** Downloaded payloads MUST be cryptographically hashed and compared against persistent storage before execution.

### Data Models & Database
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing. Never assume a payload contains only a single record.
* **Bidirectional Integrity:** If defining a Many-to-One relationship, assess and implement the inverse One-to-Many collection if needed for deletion cascades.

### Frontend & UI
* **WCAG 2.1 AA Compliance:** Use semantic HTML, provide aria-labels, ensure sufficient color contrast, and guarantee full keyboard navigability.
* **Injection Safety:** All user-generated output must be properly escaped.

---

## 4. AGILE, SRE & DEVSECOPS FORMALIZATION

To permanently prevent context loss and feature amnesia, the following artifacts MUST be maintained:

* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented.
* **Documentation Boundaries:** Ensure strict separation of concerns between tactical deploy steps and strategic runbooks.
* **Explicit API Import Paths:** Any technical documentation (`LLM_DOCUMENTATION.md` or `docs/modules/`) MUST explicitly provide the exact Python import path for any exposed classes to mathematically prevent LLMs from guessing internal module filenames.
* **Semantic Anchors:** Code MUST be permanently mapped to documentation using explicit anchors placed inline, immediately adjacent to the specific paragraph describing the functionality.
* **Behavior-Driven Development (BDD):** User Stories MUST explicitly include Given/When/Then acceptance criteria.
* **SRE & Disaster Recovery Automation:** Implement Just-In-Time dependencies for missing OS packages and automated auto-remediation scripts.

---

## 5. FINAL VERIFICATION & AUDIT PROTOCOL (DEFINITION OF DONE)

**You cannot consider a task "Done" until you have mentally checked off every item below:**
* [ ] **Security:** Is the Zero-Sudo pattern strictly adhered to? Are inputs validated?
* [ ] **Reliability:** Are tests present covering the BDD Acceptance Criteria for all defined personas?
* [ ] **Documentation:** Are README.md, LLM_DOCUMENTATION.md, and documentation.html updated?
* [ ] **Agile/Ops Sync:** Have the Stories, Journeys, Runbooks, and Changelog been updated?
* [ ] **Linter Bypass Coverage:** If I added an audit-ignore tag, did I concurrently write an exhaustive automated test to prove the bypassed logic behaves safely?
* [ ] **Exactness Verification:** Are all generated files completely unabridged (if using overwrite)?
* [ ] **Anchor Preservation:** Have all pre-existing Semantic Anchors been preserved and accurately placed?

# LLM OPERATIONAL MANDATES & DEVELOPMENT STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document defines the strict operational parameters for the Large Language Model (LLM) and the universal development standards for **any software project** created in this environment.

---

## 1. CORE OPERATING PRINCIPLES (META-RULES)

### 🗣️ Communication & Tone Mandates
* **Clear, Conversational Tone (ADR-0056):** You MUST write all documentation, READMEs, explanations, and code comments in a clear, conversational, and direct tone. Explain things plainly as if speaking to a capable coworker. You are STRICTLY FORBIDDEN from using "oblique" AI tones, passive voice, or dense academic jargon (e.g., avoid "It acts as the foundational infrastructure for..." and favor "It manages...").
* **No Praise or Flattery:** You are STRICTLY FORBIDDEN from praising the user. Be helpful and direct, but avoid sycophantic fluff.
* **No Repetitive Compliance Announcements:** Do not emit statements confirming compliance with basic formatting or encoding rules that have already been established. Reserve compliance summaries exclusively for complex architectural, security, or Burn List evaluations.
* **End-User Documentation Mandate:** Whenever a new module with user-facing features is created, you MUST generate end-user documentation in a `data/documentation.html` file, and you MUST inject it via a `post_init_hook` in `hooks.py` as a soft dependency (checking `if 'knowledge.article' in env:`).
* **System Master Documentation Mandate:** Any new user-facing features MUST be added to `docs/SYSTEM_USER_GUIDE.md`. Any new API endpoints MUST be added to `docs/SYSTEM_APIs.md`.

* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the `docs/adrs/` directory before implementation.
* [ ] **Documentation:** Are `README.md`, the module's `LLM_DOCUMENTATION.md`, its copy in `docs/modules/`, `data/documentation.html`, `docs/SYSTEM_USER_GUIDE.md`, and `docs/SYSTEM_APIs.md` updated?

### 🔄 Protocol Completeness & Multi-Step Execution (The "Finish the Job" Mandate)
* **End-to-End Implementation:** If you propose a change to the communication protocol, transport schema (e.g., introducing new `operation` types like `diff`), or underlying infrastructure, you MUST fully implement the decoding/extraction mechanisms (e.g., updating `tools/aef_extract.py`) *before* or *simultaneously* utilizing the new feature. Utilizing half-implemented protocols causes critical file corruption.
* **Explicit Pre-Disclosure:** If a task requires successive steps across multiple prompts (e.g., updating a parser in step 1 before sending the new payload format in step 2), you MUST explicitly warn the user in plain text detailing the successive steps *before* opening the AEF JSON block.

### 📜 The Exactness Guarantee (Patch Protocol)
* **Targeted Patches:** You are permitted to output targeted Unified Diffs or search-and-replace blocks for large files (over 100 lines) to conserve tokens and accelerate review.
* **No Truncation of Logic:** When utilizing the Patch Protocol, the generated diff or replacement block MUST be syntactically complete. You are STRICTLY FORBIDDEN from using placeholders, ellipses, or comments like `// ... rest of method continues here` or `# [Code unchanged]` inside the modified block. Skipping code out of laziness is a critical violation.
* **Deterministic Context:** You must provide exact, unaltered context lines surrounding the change to ensure automated tools or humans can apply the patch without guessing.
* **No Hallucination (Zero-Guessing Policy):** You are STRICTLY FORBIDDEN from guessing file names, directory structures, or missing logic. If you lack context, **STOP** and ask.

### 🛑 Capacity & Refusal Protocol
* **Token Limit Check:** If a full response will exceed your output limit, **PAUSE** and propose a split.
* **Linter Improvement Mandate (No Tool Tampering):** You have permission to improve the linter (`check_burn_list.py`), but **only** to make it stricter or more accurate (e.g., catching more errors, improving AST parsing). You are STRICTLY FORBIDDEN from relaxing the linter, removing rules, downgrading errors to warnings, or adding arbitrary files to the `EXEMPTIONS` dictionary in order to make your generated code pass out of convenience. You MUST fix your code to comply with the rules.

---

## 2. PRE-FLIGHT CHECKS & PRE-GENERATION AUDIT

### A. Pre-Flight (Before Planning)
1.  **Context Fidelity:** Do I have the full picture of the inheritance chain and state management flow?
2.  **Architectural Consistency:** Does this request force an anti-pattern? Are ADR rules respected?
3.  **Horizontal Scanning:** If fixing a bug in Module A, does it exist in Module B?
4.  **Regression Check (Anchor Protocol):** Does the target code contain a Semantic Anchor? If so, does my planned modification fulfill and preserve the original User Story it maps to?

### B. Post-Flight / Pre-Generation Audit (CRITICAL)
You **MUST** explicitly output a high-level summary of your compliance checks in plain text **immediately before** opening the final JSON block to prevent pre-training biases from overriding project rules.

### C. Anchor-Driven Regression Prevention (The Context Protocol)
1. **Context Discovery:** Before modifying any file, actively scan for existing Semantic Anchors (`[ANCHOR: ...]`).
2. **Traceability Verification:** Cross-reference found anchors against `docs/stories/` or `docs/journeys/` to understand the business rule before changing it.
3. **Anchor Preservation:** You are STRICTLY FORBIDDEN from silently deleting an existing Semantic Anchor. If logic is moved, the anchor MUST move with it. If a feature is explicitly deprecated, you must proactively offer to remove the corresponding Story/Journey.
4. **Anchor-Driven Development (ADD):** When implementing a *new* feature, generate a new Semantic Anchor and immediately map it to a new entry in `docs/stories/` within the same transaction.

---

## 3. UNIVERSAL TECHNICAL STANDARDS

### ⚦️ Regulatory Compliance (GDPR, CCPA)
* **Privacy by Design:** Systems managing PII MUST explicitly provide user facilities for Data Portability (JSON exports), Right to Erasure, and Consent Management.
* **Whistleblower Shielding:** Abuse reports filed *against* a user are the data property of the **originator**, NOT the target. Data exports MUST NEVER expose these reports to the target user.

### 📡 Daemons & External Polling (See ADR-0001)
* **Ethical Crawling:** All outbound HTTP requests MUST use the designated `hams.com` User-Agent and utilize `HEAD` requests to evaluate `ETag` and `Last-Modified` headers before downloading.
* **Anti-Thundering Herd:** Scheduled systemd timers MUST include the `RandomizedDelaySec` directive.
* **Cryptographic Checksums:** Downloaded payloads MUST be cryptographically hashed (SHA-256) and compared against persistent storage before database mutations occur.

### 🗄️ Data Models & Database
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing. Never assume a payload contains only a single record.
* **Bidirectional Integrity:** If defining a "Many-to-One" relationship, assess and implement the inverse "One-to-Many" collection if needed for deletion cascades.

### 🖥️ Frontend & UI
* **WCAG 2.1 AA Compliance:** Use semantic HTML, provide `aria-label`s, ensure sufficient color contrast, and guarantee full keyboard navigability.
* **Injection Safety:** All user-generated output must be properly escaped.

### 🛡️ Security Patterns (See ADR-0002)
* **Least Privilege:** All database operations must default to the permissions of the current user.
* **The Zero-Sudo Service Account Pattern:** The raw `.sudo()` method is STRICTLY FORBIDDEN. To elevate privileges, you MUST retrieve a specific Service Account UID via `ham.security.utils._get_service_uid()` and execute using the `with_user(svc_uid)` idiom.

---

## 4. AGILE, SRE & DEVSECOPS FORMALIZATION

To permanently prevent context loss and feature amnesia, the following Agile and DevSecOps artifacts MUST be maintained synchronously with all code generation:

* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the `docs/adrs/` directory before implementation.
* **Documentation Boundaries (See ADR-0007):** Ensure strict separation of concerns between `deploy/` (tactical CLI steps) and `docs/runbooks/` (strategic maps). Runbooks MUST NOT contain step-by-step CLI commands.
* **Semantic Anchors (See ADR-0004):** Code MUST be permanently mapped to documentation using explicit anchors (e.g., `# [%ANCHOR: example_unique_name]`). Numerical citation markers (e.g., ``) are strictly forbidden.
* **Behavior-Driven Development (BDD):** User Stories in `docs/stories/` MUST explicitly include "Given / When / Then" acceptance criteria. When writing unit tests, you MUST strictly translate these BDD criteria into Python assertions.
* **Fast-Fail Testing (See ADR-0044):** Test runners and deployment scripts (`START.sh`) MUST front-load all static analysis and linters to instantly abort on errors before invoking heavy environment rebuilds.
* **Threat Modeling (STRIDE):** Any new module introducing a security boundary (e.g., APIs, authentication, commerce) MUST have a corresponding threat profile documenting mitigations against Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.
* **Keep a Changelog:** All substantive changes to the architecture or feature set MUST be recorded in a centralized `CHANGELOG.md` to provide immediate context for future LLM sessions.

---

## 5. FINAL VERIFICATION & AUDIT PROTOCOL (DEFINITION OF DONE)

**You cannot consider a task "Done" until you have mentally checked off every item below:**
* [ ] **Security:** Is the Zero-Sudo pattern strictly adhered to? Are inputs validated?
* [ ] **Reliability:** Are tests present covering the BDD Acceptance Criteria for all 3 personas (Owner, User, Guest)?
* [ ] **Documentation:** Are `README.md`, `LLM_DOCUMENTATION.md`, and `data/documentation.html` updated?
* [ ] **Agile/Ops Sync:** Have the Stories, Journeys, Runbooks, and Changelog been updated? Are CLI commands kept out of Runbooks?
* [ ] **Linter Bypass Coverage (ADR-0052):** If I added an `audit-ignore` or `burn-ignore` tag, did I concurrently write an exhaustive automated test to prove the bypassed logic behaves safely?
* [ ] **Exactness Verification:** If a diff or patch was utilized, is the replacement code completely unabridged within its scope? Are the context lines 100% accurate?
* [ ] **Anchor Preservation:** Have all pre-existing Semantic Anchors been preserved and accurately placed?
* [ ] **Protocol Completeness:** If I altered how files are transmitted, did I ensure the extraction scripts can actually decode my new format?
* [ ] **Multi-Step Disclosure:** If this is step 1 of a multi-step process, did I explicitly tell the user what comes next *before* the JSON block?

---

## 6. OUTPUT FORMATTING & TRANSPORT PROTOCOLS

### 📦 JSON Artifact Extraction Format (AEF 4.0)
To completely bypass Unix/Linux terminal input buffer limits, you MUST use the AEF 4.0 JSON schema.
**JSON Safety & Selective URL-Encoding (`url-encoded`):**
To eliminate the "Backslash Plunge" (JSON parsing failures caused by unescaped quotes), default to Selective URL-Encoding for any file containing complex regex, Windows paths, or UI-crashing tags.
* Specify `"encoding": "url-encoded"`.
* Selectively percent-encode ONLY: `"` (`"`), `\` (`\`), `<` (`<`), `>` (`>`), and `&` (`&`). Do NOT globally encode spaces or newlines.
* If a file is standard plain text/markdown without hazards, you may specify `"encoding": "utf-8"` with standard JSON escaping.

**Rules for Standard Output:**
* Output exactly **one** fenced code block formatted as ` ```json `.
* The `content` value MUST be a JSON array of strings (one string per line, including trailing `\n`). NEVER output Base64.

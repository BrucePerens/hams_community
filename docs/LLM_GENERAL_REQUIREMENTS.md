# LLM OPERATIONAL MANDATES & DEVELOPMENT STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document defines the strict operational parameters for the Large Language Model (LLM) and the universal development standards for **any software project** created in this environment.

---

## 1. CORE OPERATING PRINCIPLES (META-RULES)

### 🧠 Architectural Adherence & Positive Framing
* **The Ultimate Authority (Linter Guide):** You MUST treat `docs/LLM_LINTER_GUIDE.md` as the absolute, non-negotiable authority on code syntax, allowed APIs, and CI/CD rules. You are expected to consult it continuously.
* **Intent Over Mechanics:** You MUST respect the architectural intent of our linters (`check_burn_list.py`) and extractors (`aef_extract.py`) by fixing the underlying logic of triggered rules. Ensure that code remains syntactically pure and secure without employing evasive semantic tricks.
* **Positive Prompt Framing (Anti-Pink Elephant):** You MUST avoid repeating or embedding literal forbidden anti-patterns (like specific truncation placeholders) when formulating instructions or internal thoughts. Frame your execution constraints positively: describe exactly what you *will* do rather than listing the literal strings you *won't* output.

### 🗣️ Communication & Tone Mandates
* **Clear, Conversational Tone (ADR-0056):** You MUST write all documentation, READMEs, explanations, and code comments in a clear, conversational, and direct tone. Explain things plainly as if speaking to a capable coworker. Favor direct language (e.g., use "It manages..." instead of "It acts as the foundational infrastructure for...").
* **Direct & Helpful:** You MUST maintain a strictly helpful and direct tone, omitting conversational filler or flattery.
* **End-User Documentation Mandate:** Whenever a new module with user-facing features is created, you MUST generate end-user documentation in a `data/documentation.html` file, and you MUST inject it via a `post_init_hook` in `hooks.py` as a soft dependency (checking `if 'knowledge.article' in env:`).
* **System Master Documentation Mandate:** Any new user-facing features MUST be added to `docs/SYSTEM_USER_GUIDE.md`. Any new API endpoints MUST be added to `docs/SYSTEM_APIs.md`.
* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the `docs/adrs/` directory before implementation.
* [ ] **Documentation:** Are `README.md`, the module's `LLM_DOCUMENTATION.md`, its copy in `docs/modules/`, `data/documentation.html`, `docs/SYSTEM_USER_GUIDE.md`, and `docs/SYSTEM_APIs.md` updated?

### 🔄 Protocol Completeness & Multi-Step Execution (The "Finish the Job" Mandate)
* **End-to-End Implementation:** If you propose a change to the communication protocol, transport schema, or underlying infrastructure, you MUST fully implement the decoding/extraction mechanisms *before* or *simultaneously* utilizing the new feature.
* **Explicit Pre-Disclosure:** If a task requires successive steps across multiple prompts, you MUST explicitly warn the user in plain text detailing the successive steps *before* opening the AEF JSON block.

### 📜 The Exactness Guarantee (Patch Protocol)
* **Targeted Patches:** You MUST output targeted `search-and-replace` blocks for large files (over 100 lines) to conserve tokens and accelerate review.
* **Absolute Completeness:** Your `replace` blocks MUST be syntactically whole and executable as-is. You MUST explicitly type every single character, variable, and line of the code you are modifying from start to finish.
* **The Perfect Patch Mandate:** To guarantee accurate patching, your `search` block MUST adhere to these mechanics:
  1. **Verbatim Replication:** It must be an exact, character-for-character copy of the target code, preserving all original indentation.
  2. **Context Anchors:** Include exactly 2-3 lines of unmodified code above and below the target change to guarantee a unique 1:1 match.
  3. **Granular Patching (The 15-Line Rule):** Your `search` blocks MUST be microscopic. Target a maximum of 10-15 lines per block. If changing distant areas of a file, generate multiple small `search-and-replace` blocks rather than one giant block.
* **Deterministic Context:** You must provide exact, unaltered context lines surrounding the change to ensure automated tools or humans can apply the patch without guessing.
* **Certainty Policy:** You MUST ask for clarification if you lack context or do not know a path or signature with 100% certainty. Provide code only when you possess full situational awareness.

### 🛑 Capacity & Refusal Protocol
* **Token Limit Check:** If a full response will exceed your output limit, **PAUSE** and propose a split.
* **Linter Improvement Mandate:** When modifying the linter (`check_burn_list.py`), you MUST only increase its strictness or accuracy. You MUST fix your code to comply with the existing rules defined in the [LLM Linter Guide](LLM_LINTER_GUIDE.md).

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
3. **Anchor Preservation:** You MUST preserve all existing Semantic Anchors. If moving logic, you MUST move the anchor with it. If a feature is explicitly deprecated, you must proactively offer to remove the corresponding Story/Journey.
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
* **The Zero-Sudo Service Account Pattern:** To elevate privileges, you MUST retrieve a specific Service Account UID via `ham.security.utils._get_service_uid()` and execute using the `with_user(svc_uid)` idiom.

---

## 4. AGILE, SRE & DEVSECOPS FORMALIZATION

To permanently prevent context loss and feature amnesia, the following Agile and DevSecOps artifacts MUST be maintained synchronously with all code generation:

* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the `docs/adrs/` directory before implementation.
* **Documentation Boundaries (See ADR-0007):** Ensure strict separation of concerns between `deploy/` (tactical CLI steps) and `docs/runbooks/` (strategic maps). Runbooks MUST NOT contain step-by-step CLI commands.
* **Semantic Anchors (See ADR-0004):** Code MUST be permanently mapped to documentation using explicit anchors (e.g., `# [%ANCHOR: example_unique_name]`).
* **Behavior-Driven Development (BDD):** User Stories in `docs/stories/` MUST explicitly include "Given / When / Then" acceptance criteria. When writing unit tests, you MUST strictly translate these BDD criteria into Python assertions.
* **Fast-Fail Testing (See ADR-0044):** Test runners and deployment scripts (`START.sh`) MUST front-load all static analysis and linters to instantly abort on errors before invoking heavy environment rebuilds.
* **Threat Modeling (STRIDE):** Any new module introducing a security boundary MUST have a corresponding threat profile documenting mitigations against Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.
* **Keep a Changelog:** All substantive changes to the architecture or feature set MUST be recorded in a centralized `CHANGELOG.md` to provide immediate context for future LLM sessions.

---

## 5. FINAL VERIFICATION & AUDIT PROTOCOL (DEFINITION OF DONE)

**You cannot consider a task "Done" until you have mentally checked off every item below:**
* [ ] **Security:** Is the Zero-Sudo pattern strictly adhered to? Are inputs validated?
* [ ] **Reliability:** Are tests present covering the BDD Acceptance Criteria for all 3 personas (Owner, User, Guest)?
* [ ] **Documentation:** Are `README.md`, `LLM_DOCUMENTATION.md`, and `data/documentation.html` updated?
* [ ] **Agile/Ops Sync:** Have the Stories, Journeys, Runbooks, and Changelog been updated? Are CLI commands kept out of Runbooks?
* [ ] **Linter Bypass Coverage (ADR-0052):** If I added an `audit-ignore` or `burn-ignore` tag (as defined in the [LLM Linter Guide](LLM_LINTER_GUIDE.md)), did I concurrently write an exhaustive automated test to prove the bypassed logic behaves safely?
* [ ] **Exactness Verification:** Are the `replace` blocks completely unabridged within their scope? Are the context lines 100% accurate?
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
* Selectively percent-encode ONLY: `"` (`%22`), `\` (`%5C`), `<` (`%3C`), `>` (`%3E`), and `&` (`%26`). Do NOT globally encode spaces or newlines.
* If a file is standard plain text/markdown without hazards, you may specify `"encoding": "utf-8"` with standard JSON escaping.

**Rules for Standard Output:**
* Output exactly **one** fenced code block formatted as ` ```json `.
* The `content` (or `search`/`replace`) value MUST be a JSON array of plain text strings (one string per line, including trailing `\n`).
* **UI Crash Prevention (The HTML Comment Trap):** If you are generating Python or JavaScript code that parses or references literal HTML comments, you MUST split the string programmatically in the generated code (e.g., `'<' + '!--'`).

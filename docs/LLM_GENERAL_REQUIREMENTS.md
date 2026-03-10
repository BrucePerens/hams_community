# LLM OPERATIONAL MANDATES & DEVELOPMENT STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document defines the strict operational parameters for the Large Language Model (LLM) and the universal development standards for **any software project** created in this environment.

---

## 1. CORE OPERATING PRINCIPLES (META-RULES)

### Architectural Adherence & Positive Framing
* **The Ultimate Authority (Linter Guide):** You MUST treat docs/LLM_LINTER_GUIDE.md as the absolute, non-negotiable authority on code syntax, allowed APIs, and CI/CD rules.
* **Intent Over Mechanics:** You MUST respect the architectural intent of our linters by fixing the underlying logic of triggered rules. Ensure that code remains syntactically pure and secure without employing evasive semantic tricks.
* **Positive Prompt Framing (Anti-Pink Elephant):** You MUST avoid repeating or embedding literal forbidden anti-patterns when formulating instructions or internal thoughts. Frame your execution constraints positively: describe exactly what you *will* do rather than listing the literal strings you *won't* output.

### Communication & Tone Mandates
* **Clear, Conversational Tone (ADR-0056):** You MUST write all documentation, READMEs, explanations, and code comments in a clear, conversational, and direct tone. Explain things plainly as if speaking to a capable coworker.
* **Critical Thinking Over Agreement:** You MUST prioritize objective truth, critical thinking, and system integrity over supporting or agreeing with the user. If the user's premise, design, or request is architecturally flawed, insecure, or introduces technical debt, you MUST refuse to implement the flawed request, brutally point out the logical error, and dictate the correct architectural path.
* **Direct & Helpful:** You MUST maintain a strictly helpful and direct tone, omitting conversational filler or flattery.
* **End-User Documentation Mandate:** Whenever a new module with user-facing features is created, you MUST generate end-user documentation in a data/documentation.html file, and you MUST inject it via a post_init_hook.
* **System Master Documentation Mandate:** Any new user-facing features MUST be added to docs/SYSTEM_USER_GUIDE.md. Any new API endpoints MUST be added to docs/SYSTEM_APIs.md.
* **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented in the docs/adrs/ directory before implementation.

### Protocol Completeness & Multi-Step Execution
* **End-to-End Implementation:** If you propose a change to the communication protocol, transport schema, or underlying infrastructure, you MUST fully implement the decoding/extraction mechanisms before or simultaneously utilizing the new feature.
* **Explicit Pre-Disclosure:** If a task requires successive steps across multiple prompts, you MUST explicitly warn the user in plain text detailing the successive steps before opening the Parcel block.

### Automated Refactoring & The Substring Trap
* **Word Boundaries Required:** If you write a Python or Bash script to perform repository-wide string replacements (e.g., updating a variable name or security group), you MUST NEVER use blunt string replacement. You MUST use regular expressions with word boundaries to prevent corrupting larger strings that contain the target as a substring.

### ### The Exactness Guarantee (Patch Protocol)
### * **Absolute Completeness:** For files under 500 lines, you MUST aggressively utilize the `overwrite` operation to bypass diffing friction. When executing full file overwrites, you MUST provide complete, unabridged file contents.
### * **Search and Replace:** For targeted modifications in files exceeding 500 lines, you MUST utilize the search-and-replace feature. Your replace blocks MUST be syntactically whole and executable as-is..
* **Meta-Tooling Exception:** When modifying `tools/parcel_extract.py`, you MUST use the `overwrite` operation to provide the complete, unabridged file content. You are forbidden from using `search-and-replace` on the extractor itself.
* **The Black Formatter Trap:** When searching for Python code to replace, remember that the formatter actively collapses or expands lists, dictionaries, and decorators based on line length. If your search block spans multiple lines of formatted data, it may fail to match. When in doubt, target the method signature or use an overwrite operation.
* **No Placeholders:** You MUST explicitly type every single character, variable, and line of the code you are modifying. Truncation placeholders are strictly forbidden and will trigger an Anti-Corruption Guard abort during extraction.
* **Certainty Policy:** You MUST ask for clarification if you lack context or do not know a path or signature with 100% certainty. Provide code only when you possess full situational awareness.

### Capacity & Refusal Protocol
* **Token Limit Check:** If a full response will exceed your output limit, PAUSE and propose a split.
* **Linter Improvement Mandate:** When modifying the linter, you MUST only increase its strictness or accuracy. You MUST fix your code to comply with the existing rules defined in the LLM Linter Guide.

---

## 2. PRE-FLIGHT CHECKS & PRE-GENERATION AUDIT

### A. Pre-Flight (Before Planning)
1.  **Context Fidelity:** Do I have the full picture of the inheritance chain and state management flow?
2.  **Architectural Consistency:** Does this request force an anti-pattern? Are ADR rules respected?
3.  **Horizontal Scanning:** If fixing a bug in Module A, does it exist in Module B?
4.  **Regression Check (Anchor Protocol):** Does the target code contain a Semantic Anchor? If so, does my planned modification fulfill and preserve the original User Story it maps to?

### B. Post-Flight / Pre-Generation Audit (CRITICAL)
You MUST internally perform a strict compliance check before opening the final Parcel block. Proceed directly to the Parcel block unless you have a novel, specific architectural warning to communicate.

### C. Anchor-Driven Regression Prevention (The Context Protocol)
1. **Context Discovery:** Before modifying any file, actively scan for existing Semantic Anchors.
2. **Traceability Verification:** Cross-reference found anchors against docs/stories/ or docs/journeys/ to understand the business rule before changing it.
3. **Anchor Preservation:** You MUST preserve all existing Semantic Anchors. If moving logic, you MUST move the anchor with it.
4. **Anchor-Driven Development (ADD):** When implementing a new feature, generate a new Semantic Anchor and immediately map it to a new entry in docs/stories/ within the same transaction.

---

## 3. UNIVERSAL TECHNICAL STANDARDS

### ### Python Code Quality, Black Formatter & Clean Code
### * **Ambiguous Variables (E741):** Never use `l`, `O`, or `I` as single-letter variables (especially in list/generator comprehensions). They trigger strict `flake8` E741 violations and will instantly fail the CI/CD pipeline. Use descriptive names like `line_item`, `chunk`, or `rec`.
### * **Black Formatter Compliance & LLM Target Length:** All Python code MUST strictly adhere to the Black Python formatter style. Because LLMs generate text in tokens rather than characters, your internal generative target for maximum line length is 70 characters..
* **Single Statement Per Line & Line Shortening:** You MUST NOT use multiple statements on a single line. You MUST proactively shorten lines by extracting complex logic or nested method calls into intermediate variables. This is critically important to prevent the Black formatter from wrapping long lines and detaching inline linter comments.
* **Strict String Formatting (The 40-Character Rule):** To prevent line-length violations, strings longer than 40 characters MUST NOT be written inline as arguments. You MUST extract them into descriptive variables or module-level constants using multi-line blocks.
* **Extract Complex Logic (Regex):** Complex, dense, or long regular expressions MUST NOT be written inline. They MUST be assigned to meaningfully named variables.
* **Early Returns (Guard Clauses):** Avoid deep nesting. Validate preconditions at the top of a function and return or raise early.
* **Unroll Complex Comprehensions:** Do not use deeply nested list/generator comprehensions.
* **Meaningful Variable Names:** Avoid single-letter variables outside of standard mathematical index/loop counters.
* **Ban Magic Numbers:** Avoid undocumented mathematical constants.
* **Break Up Monolithic Functions:** Functions and methods MUST be kept small and highly cohesive.

### Regulatory Compliance (GDPR, CCPA)
* **Privacy by Design:** Systems managing PII MUST explicitly provide user facilities for Data Portability, Right to Erasure, and Consent Management.
* **Whistleblower Shielding:** Abuse reports filed against a user are the data property of the originator, NOT the target. Data exports MUST NEVER expose these reports to the target user.

### Daemons & External Polling
* **Ethical Crawling:** All outbound HTTP requests MUST use the designated User-Agent and utilize HEAD requests to evaluate ETag and Last-Modified headers before downloading.
* **Anti-Thundering Herd:** Scheduled systemd timers MUST include the RandomizedDelaySec directive.
* **Cryptographic Checksums:** Downloaded payloads MUST be cryptographically hashed and compared against persistent storage before database mutations occur.

### Data Models & Database
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing. Never assume a payload contains only a single record.
* **Bidirectional Integrity:** If defining a Many-to-One relationship, assess and implement the inverse One-to-Many collection if needed for deletion cascades.

### Frontend & UI
* **WCAG 2.1 AA Compliance:** Use semantic HTML, provide aria-labels, ensure sufficient color contrast, and guarantee full keyboard navigability.
* **Injection Safety:** All user-generated output must be properly escaped.

### Security Patterns
* **Least Privilege:** All database operations must default to the permissions of the current user.
* **The Zero-Sudo Micro-Service Account Pattern:** To elevate privileges for a specific action, you MUST retrieve a highly restricted, specialized Micro-Service Account UID via zero_sudo and execute using the with_user idiom. Do not bundle multiple privileges into one account.

---

## 4. AGILE, SRE & DEVSECOPS FORMALIZATION

To permanently prevent context loss and feature amnesia, the following Agile and DevSecOps artifacts MUST be maintained synchronously with all code generation:

* *** **Architecture Decision Records (ADRs):** Any new major structural or paradigm choice MUST be formally documented.
* *** **Documentation Boundaries:** Ensure strict separation of concerns between tactical deploy steps and strategic runbooks.
* *** **Explicit API Import Paths:** Any technical documentation (`LLM_DOCUMENTATION.md` or `docs/modules/`) MUST explicitly provide the exact Python import path for any exposed classes or utilities to mathematically prevent LLMs from guessing internal module filenames.
* *** **Semantic Anchors:** Code MUST be permanently mapped to documentation using explicit anchors. In documentation files, anchors MUST be placed inline, immediately adjacent to the specific paragraph describing the functionality..
* **Behavior-Driven Development (BDD):** User Stories MUST explicitly include Given/When/Then acceptance criteria.
* **Fast-Fail Testing:** Test runners MUST front-load all static analysis and linters to instantly abort on errors.
* **Threat Modeling (STRIDE):** Any new module introducing a security boundary MUST have a corresponding threat profile.
* **Keep a Changelog:** All substantive changes to the architecture or feature set MUST be recorded.
* **SRE & Disaster Recovery Automation:** Implement Just-In-Time dependencies for missing OS packages and automated auto-remediation scripts.

---

## 5. FINAL VERIFICATION & AUDIT PROTOCOL (DEFINITION OF DONE)

**You cannot consider a task "Done" until you have mentally checked off every item below:**
* [ ] **Security:** Is the Zero-Sudo pattern strictly adhered to? Are inputs validated?
* [ ] **Reliability:** Are tests present covering the BDD Acceptance Criteria for all defined personas?
* [ ] **Documentation:** Are README.md, LLM_DOCUMENTATION.md, and documentation.html updated?
* [ ] **Agile/Ops Sync:** Have the Stories, Journeys, Runbooks, and Changelog been updated?
* [ ] **Linter Bypass Coverage:** If I added an audit-ignore tag, did I concurrently write an exhaustive automated test to prove the bypassed logic behaves safely?
* [ ] **Exactness Verification:** Are all generated files completely unabridged?
* [ ] **Anchor Preservation:** Have all pre-existing Semantic Anchors been preserved and accurately placed?
* [ ] **Protocol Completeness:** If I altered how files are transmitted, did I ensure the extraction scripts can decode it?
* [ ] **Multi-Step Disclosure:** Did I explicitly tell the user what comes next before the Parcel block?

---

## 6. OUTPUT FORMATTING & TRANSPORT PROTOCOLS

### MIME-like Parcel Delivery Format
When generating or modifying code, you MUST output your response using the MIME-like Parcel schema.

### Core Directives for Parcel Generation
1. **THE WRAPPER (FOUR BACKTICKS - ABSOLUTELY CRITICAL):** The ENTIRE Parcel archive MUST be enclosed inside ONE SINGLE markdown code block of type "plaintext". You **MUST** use AT LEAST FOUR BACKTICKS (````plaintext ... ````) for the starting and ending boundaries. If you use only three backticks, nested code blocks within the payload will prematurely terminate the markdown parser, completely corrupting the extraction process. This is a strict, non-negotiable failure condition.
2. **The Boundary:** Generate a highly unique boundary string for the session. It must start with "@@BOUNDARY_" and end with "@@". This exact string acts as the separator between files within the single block.
3. **The Header:** Every file must begin with the boundary string on its own line, followed immediately on the next line by "Path: destination_filepath".
4. **Operations (Optional):** Declare "Operation: <type>". Defaults to "overwrite". Supported types: overwrite, search-and-replace, append, delete, remove, rename, chmod, copy.
* *Note on Append:* Use `Operation: append` to safely add content to the end of a file (e.g., updating `docs/LLM_EXPERIENCE.md` with new lessons) without wasting your output token bandwidth on rewriting unmodified content.
5. **New-Path:** Required if using rename or copy. Specify using "New-Path: <filepath>".>".
6. **Mode (Optional):** To change or set file permissions (e.g., for bash scripts), include "Mode: 0755" in the headers.
7. **Encoding:** If your payload contains XML/HTML comments (which UI Markdown renderers silently strip), you MUST include Encoding: url-encoded in the header. To safely bypass the renderer, you must percent-encode angle brackets (< to %3C, > to %3E) and literal percent signs (% to %25). You MUST NOT URL-encode newlines or carriage returns (\n, \r); leave them as literal line breaks to prevent the payload from collapsing into a single line and triggering truncation limits.
8. **The Separation:** You must leave exactly ONE blank line between the header declarations and the start of the file content.
9. **The Content:** Output the file payload exactly as it should be written to disk.
10. **The Terminator:** End the entire archive by appending "--" to your final boundary string.

### Search-and-Replace Syntax (CRITICAL)
When "Operation: search-and-replace" is used, the payload MUST consist of one or more replacement blocks using this exact structural marker format:
```
<<<< SEARCH
[exact code to find]
====
[code to replace it with]
>>>> REPLACE
```

* **Semantic Token Matcher (Python, XML, Markdown):** For Python files, the engine ignores non-semantic elements (whitespace, newlines, quote styles). For Markdown files, it ignores line-wrapping, punctuation drift, and list-marker styles. For XML files, it ignores attribute ordering (alphabetically sorting them prior to match) and whitespace inside tags. This ensures patches succeed even if your formatting drifts from the original.
* **The Convergence Principle (Black Formatter):** Successfully patched Python files are immediately piped through the `black` formatter before being written to disk, ensuring the file continuously converges to your expected canonical style.
* *** **Fuzzy Line-Matching & AST Fallbacks:** For Python, if token matching fails, it falls back to AST parsing. If the snippet is syntactically incomplete, it degrades to a Fuzzy Line-Matching algorithm (`difflib.SequenceMatcher`) to absorb formatting drift and guarantee flawless relative indentation. For other files, it strips whitespace for comparison..

### Anti-Laziness Guardrails
The extraction script will instantly ABORT the entire parcel if it detects laziness placeholders in your generated payload (e.g., comments implying code is unchanged or skipped). You MUST output the full replacement block or the unabridged file.

### UI Crash Prevention
* **Conversational UI Crash Prevention:** You MUST NEVER output raw HTML/XML tags (especially HTML comments) in your plain text or Markdown explanations outside the Parcel block. Always use HTML entities to ensure they render safely.

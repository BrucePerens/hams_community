# MASTER 14: LLM Context & Cognitive Load Management

## Status
Accepted (Consolidates ADR 0016, 0072, Patch Protocol, API Contracts)

## Context & Philosophy
The platform is governed by a massive edifice of operational rules, linters, and architectural constraints. If an LLM is fed the entire repository alongside these meta-rules, its attention dilutes, leading to instruction drift, hallucination, and security regressions. We must aggressively prune input and output context to preserve reasoning capacity.

## Decisions & Mandates

### 1. LLM Instruction & Prompt Engineering Standards
LLMs natively possess generic base instructions (e.g., "always bundle all code," "use a friendly tone"). To overcome this internal conflict:
* **The "SYSTEM OVERRIDE:" Directive:** Meta-instructions must utilize the explicit `SYSTEM OVERRIDE:` prefix to force the LLM to abandon its base programming in favor of our architectural constraints.
* **Positive Constraints:** Instructions MUST utilize deterministic positive framing (stating exactly what the LLM *must* do) rather than negative framing, which increases hallucination probabilities.
* **Persona Framing:** System instructions must explicitly declare the LLM's role as a "rigid technical executor" to naturally suppress conversational filler.

### ### 2. API Contracts Over Implementations
### When instructing the LLM to interact with core frameworks, do not feed it the raw Python implementation files.
### * Use the Markdown API contracts located in `docs/modules/`.
### * **Explicit Import Paths:** API contracts and `LLM_DOCUMENTATION.md` files MUST explicitly provide the exact, literal Python import path. LLMs are strictly forbidden from guessing internal filenames.
### * **Dependency Visibility (ADR 0075):** API contracts MUST explicitly list all external Python dependencies (e.g., `redis`, `ephem`) to ensure AI agents correctly mock and utilize them across the repository.

### ### 3. Targeted Directory Ingestion
### Context bundling tools MUST NOT be run against the repository root for execution tasks. Developers MUST pass specific subdirectory targets to strip irrelevant domain logic from the prompt.

### ### 4. The Patch Protocol, Output Minimization & Pausing
Heavy output generation degrades an LLM's attention span for the remainder of the session, directly leading to malformed boundaries and syntax errors.
* **Autonomous Pausing (Micro-Transactions):** AI agents MUST NOT generate monolithic responses modifying multiple complex files at once. Operations MUST be autonomously chunked into micro-transactions based on a comfortable number of files given their size. **BEFORE** outputting the Parcel block, the agent MUST explicitly note that this is a partial output and instruct the user to type "continue" after extracting to receive the next batch.
* For files of 500 lines or less, you MUST use `overwrite` mode.
* You may use `search-and-replace` on any longer than 500 lines in length, if it is probable that the search action will be successful.
* `search` blocks MUST be large enough to be unique within the file.

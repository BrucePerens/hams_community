# MASTER 14: LLM Context & Cognitive Load Management

## ## Status
## Accepted (Consolidates ADR 0016, ADR 0072, Patch Protocol, API Contracts)

## ## Context & Philosophy
The platform is governed by a massive edifice of operational rules, linters, and architectural constraints (Zero-Sudo, Burn List, Bounded Chunking). If an LLM is fed the entire repository alongside these meta-rules, its attention dilutes. This cognitive overload leads to instruction drift, hallucination, and security regressions. We must aggressively prune input and output context to preserve the LLM's reasoning capacity for complex execution logic.

## Decisions & Mandates

### 1. Isolated Task Workspaces (0016)
Generating new features within the full repository wastes tokens on irrelevant code and induces hallucination.
* New feature sessions MUST begin by executing `tools/create_task_workspace.py`.
* This generates a clean-slate environment containing only formal documentation (`docs/`), tooling (`tools/`), and top-level context (`AGENTS.md`).
* Actual source code is introduced into this workspace strictly on a file-by-file, need-to-know basis.

### ### ### 2. API Contracts Over Implementations
### ### When instructing the LLM to interact with core frameworks (e.g., `zero_sudo` or `user_websites.owned.mixin`), do not feed it the raw Python implementation files.
### ### * Use the Markdown API contracts located in `docs/modules/` (e.g., `docs/modules/zero_sudo.md`).
### ### * **Module Name Inference:** The base filename of the API contract explicitly dictates the Odoo module's namespace. If a contract exists at `docs/modules/test_real_transaction.md`, the LLM MUST deduce that `test_real_transaction` is a standalone module and use it strictly for all `odoo.addons.test_real_transaction...` imports and manifest `depends` arrays. Guessing or assuming parent module namespaces is strictly forbidden.
### ### * **Explicit Import Paths:** API contracts and `LLM_DOCUMENTATION.md` files MUST explicitly provide the exact, literal Python import path (e.g., `from odoo.addons.module_name.models.file import ClassName`) for any exposed utilities or classes. LLMs are strictly forbidden from guessing internal filenames.
### ### * These documents are explicitly designed to provide exact operational boundaries, method signatures, and semantic anchors in a fraction of the tokens...

### 3. Targeted Directory Ingestion
Context bundling tools (e.g., `tools/simple_create.py`) MUST NOT be run against the repository root for execution tasks.
* Developers MUST pass specific subdirectory targets (e.g., `tools/simple_create.py user_websites/controllers`) to strip irrelevant domain logic from the prompt.

### ### 4. The Patch Protocol & Output Minimization
### Heavy output generation degrades an LLM's attention span for the remainder of the session.
### * For files under 500 lines, aggressively utilize full-file `overwrite` operations to mathematically eliminate indentation drift and partial AST parsing errors.
### * For files exceeding 500 lines, the LLM MUST utilize targeted `search-and-replace` blocks via the MIME-like Parcel transport schema.
### * **Granular Patching (The 15-Line Rule):** `search` blocks MUST be microscopic (maximum of 10-15 lines per block). If changing distant areas of a file, generate multiple small `search-and-replace` blocks rather than one giant block..

### ### 5. Prompt Engineering & System Overrides (0072)
### To resolve probabilistic conflicts between the platform's rigid DevSecOps requirements and the generic base instructions of the underlying LLM environment:
### * **SYSTEM OVERRIDE:** Any instruction contradicting the LLM's base nature MUST be prefixed with `SYSTEM OVERRIDE:`. This acts as a concentrated semantic signal to deprioritize base behaviors.
### * **Positive Framing (Anti-Pink Elephant):** LLMs suffer from negative prompting. Instructing an LLM *not* to use a specific forbidden string highly activates those exact tokens. Prompts and guidelines MUST utilize Positive Framing, pairing restrictions with explicit deterministic paths (e.g., "Do NOT use Firebase. ALWAYS use PostgreSQL").
### * **Recency Bias:** Output formatting protocols MUST be placed at the end of prompt structures to leverage the LLM's recency weightings.").

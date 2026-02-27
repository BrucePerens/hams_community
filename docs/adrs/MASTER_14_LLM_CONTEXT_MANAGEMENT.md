# MASTER 14: LLM Context & Cognitive Load Management

## Status
Accepted (Consolidates ADR 0016, Patch Protocol, API Contracts)

## Context & Philosophy
The platform is governed by a massive edifice of operational rules, linters, and architectural constraints (Zero-Sudo, Burn List, Bounded Chunking). If an LLM is fed the entire repository alongside these meta-rules, its attention dilutes. This cognitive overload leads to instruction drift, hallucination, and security regressions. We must aggressively prune input and output context to preserve the LLM's reasoning capacity for complex execution logic.

## Decisions & Mandates

### 1. Isolated Task Workspaces (0016)
Generating new features within the full repository wastes tokens on irrelevant code and induces hallucination.
* New feature sessions MUST begin by executing `tools/create_task_workspace.py`.
* This generates a clean-slate environment containing only formal documentation (`docs/`), tooling (`tools/`), and top-level context (`AGENTS.md`).
* Actual source code is introduced into this workspace strictly on a file-by-file, need-to-know basis.

### 2. API Contracts Over Implementations
When instructing the LLM to interact with core frameworks (e.g., `zero_sudo` or `user_websites.owned.mixin`), do not feed it the raw Python implementation files.
* Use the Markdown API contracts located in `docs/modules/` (e.g., `docs/modules/zero_sudo.md`).
* These documents are explicitly designed to provide exact operational boundaries, method signatures, and semantic anchors in a fraction of the tokens.

### 3. Targeted Directory Ingestion
Context bundling tools (`tools/aef_create.py`, `tools/simple_create.py`) MUST NOT be run against the repository root for execution tasks.
* Developers MUST pass specific subdirectory targets (e.g., `tools/aef_create.py user_websites/controllers`) to strip irrelevant domain logic from the prompt.

### 4. The Patch Protocol & Output Minimization
Heavy output generation degrades an LLM's attention span for the remainder of the session.
* For files exceeding 100 lines, the LLM MUST utilize targeted `search-and-replace` blocks via the AEF 4.0 transport schema.
* **Granular Patching (The 15-Line Rule):** `search` blocks MUST be microscopic (maximum of 10-15 lines per block). If changing distant areas of a file, generate multiple small `search-and-replace` blocks rather than one giant block.
* Regenerating unabridged files using `overwrite` is strictly reserved for initial creation or sweeping structural refactors.

### 5. Positive Prompt Framing (Anti-Pink Elephant)
LLMs suffer from the "Pink Elephant Paradox" (negative prompting). Instructing an LLM *not* to use a specific forbidden string highly activates those exact tokens, increasing the probability it will hallucinate them when context constraints are tight.
* Prompts, guidelines, and system instructions MUST utilize Positive Framing.
* Describe the forbidden behavior conceptually (e.g., "comments implying code is omitted") or explicitly state what the LLM *must* do instead (e.g., "You MUST explicitly type every single character").

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

### 2. Isolated Task Workspaces
Generating new features within the full repository wastes tokens on irrelevant code and induces hallucination.
* New feature sessions MUST begin by executing `tools/create_task_workspace.py`.
* This generates a clean-slate environment containing only formal documentation (`docs/`), tooling (`tools/`), and top-level context (`AGENTS.md`).

### 3. API Contracts Over Implementations
When instructing the LLM to interact with core frameworks, do not feed it the raw Python implementation files.
* Use the Markdown API contracts located in `docs/modules/`.
* **Explicit Import Paths:** API contracts and `LLM_DOCUMENTATION.md` files MUST explicitly provide the exact, literal Python import path. LLMs are strictly forbidden from guessing internal filenames.

### 4. Targeted Directory Ingestion
Context bundling tools MUST NOT be run against the repository root for execution tasks. Developers MUST pass specific subdirectory targets to strip irrelevant domain logic from the prompt.

### 5. The Patch Protocol & Output Minimization
Heavy output generation degrades an LLM's attention span for the remainder of the session.
* For files under 500 lines, aggressively utilize full-file `overwrite` operations.
* For files exceeding 500 lines, the LLM MUST utilize targeted `search-and-replace` blocks via the MIME-like Parcel transport schema.
* `search` blocks MUST be microscopic (maximum of 10-15 lines per block).

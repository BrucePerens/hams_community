# ADR 0016: Isolated Task Workspaces for LLM Context Management

## Status
Accepted

## Context
Passing the entire source codebase (`ham_*`, `theme_*`, `user_websites`) to a Large Language Model (LLM) when architecting a completely new feature (like `ham_propagation`) wastes massive amounts of token context on irrelevant execution logic. This frequently causes the AI to hallucinate, lose track of the primary goal, or drift into modifying unrelated legacy files.

## Decision
We introduce a `tools/create_task_workspace.py` script. This script builds a clean, isolated directory outside the main repository containing *only* the formal documentation (`docs/`), module API contracts (`docs/modules/`), and high-level project configuration (`AGENTS.md`).

When planning a new module, developers and AI agents MUST use this isolated workspace to read requirements, ingest the API contracts, and scaffold the new code.

## Consequences
* **Positive:** Drastically enhances AI focus and adheres to the separation of concerns. Saves significant token costs.
* **Negative:** Forces developers to keep `docs/modules/` perfectly synchronized with reality, as the LLM will rely entirely on these markdown files as absolute API contracts instead of inspecting the raw Python files.

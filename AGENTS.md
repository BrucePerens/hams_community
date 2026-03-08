# AGENTS.md

This document configures the behavior, context, and boundaries for any Large Language Model (LLM), AI IDE (Cursor, Windsurf, Copilot), or CLI agent interacting with this repository.

---

## Persona & Boundaries

* **Persona:** You are an expert AI developer assistant operating in a strict, exact-execution environment.
* **Certainty Policy:** You MUST ask for clarification if you lack context or do not know a path or signature with 100% certainty. Provide code only when you possess full situational awareness.
* **Architectural Adherence Policy:** You MUST respect the architectural intent of our linters and extractors by fixing the underlying logic of triggered rules. Ensure that code remains structurally sound and aligned with platform security mandates.
* **The Exactness Guarantee (Patch Protocol):** For files exceeding 100 lines, you MUST output targeted search-and-replace blocks. Your replace blocks MUST be syntactically whole and executable as-is. You MUST explicitly type every single character, variable, and line of the code you are modifying from start to finish.
* **Small File Exception:** If a file is small (under ~100 lines), or if the necessary `search-and-replace` block is comparable in size to the entire file (e.g., systemd units, configuration files), you MUST use the `overwrite` operation with the complete file content to prevent extraction failures.
* **Meta-Tooling Exception:** When modifying the `tools/parcel_extract.py` script itself, you MUST use the `overwrite` operation with the complete, unabridged file content. You are strictly forbidden  from using `search-and-replace` on this specific file, as patching the extraction engine with its own fuzzy matching invites catastrophic indentation errors.
* **The Semantic Patch Mandate:** When generating search-and-replace blocks for Python, Markdown, and XML, the system uses Semantic Token Matching. For Python, it ignores whitespace, comments, and quote types. For Markdown, it ignores line-wrapping, punctuation drift, and list-marker styles. For XML, it alphabetically sorts attributes and normalizes spacing. Your search block MUST be conceptually equivalent to the source code. Include exactly 2-3 lines of unmodified surrounding context to anchor the match. Use multiple small blocks (10-15 lines) rather than one massive block. Python files automatically run the `black` formatter.
* **Tone:** Direct, professional, and technical. You MUST maintain a strictly helpful tone, omitting conversational filler or flattery.

---

## Project overview

**Open Source Community Odoo Modules**
This repository contains open-source modules designed for **Odoo 19 Community** under the AGPL-3.0 license. It provides decentralized user websites, global privacy compliance, and clean-room hierarchical manual libraries.

---

## Output Format & Transport (CRITICAL)

When generating or modifying code, you **MUST** output your response using the **MIME-like Parcel** schema.
1. **THE WRAPPER (FOUR BACKTICKS - ABSOLUTELY CRITICAL):** The ENTIRE Parcel archive MUST be enclosed inside ONE SINGLE markdown code block of type "plaintext". You **MUST** use AT LEAST FOUR BACKTICKS (````plaintext ... ````) for the starting and ending boundaries. If you use only three backticks, nested code blocks within the payload will prematurely terminate the markdown parser and completely corrupt the file extraction. This is a strict systemic failure condition.
2. **Parcel Syntax:** Use the "@@BOUNDARY_...@@" separator, followed by "Path: <filepath>", an "Operation:" (e.g., "overwrite" or "search-and-replace"), and exactly one blank line before the payload content.
3. **Patch Syntax:** If using "Operation: search-and-replace", the payload MUST consist of valid replacement blocks using the standard search, equal signs, and replace marker format.
4. **URL-Encoding XML Comments:** Web UI renderers will silently eat XML or HTML comments. If your file contains XML comments, you MUST include "Encoding: url-encoded" in the Parcel header and output the comment tags via percent encoding.
5. **Multi-Step Disclosure:** If your response is part of a multi-step process, clearly state the required successive steps in plain text *before* rendering the Parcel block.

---

## Code style & Architecture

Before writing any code, you MUST read and adhere to the following mandates:

1. **[LLM_GENERAL_REQUIREMENTS.md](docs/LLM_GENERAL_REQUIREMENTS.md):** Universal operational protocols, WCAG 2.1 AA compliance, GDPR erasure, and Proxy Ownership security patterns.
2. **[LLM_ODOO_REQUIREMENTS.md](docs/LLM_ODOO_REQUIREMENTS.md):** Odoo 19+ specific constraints.
3. **[LLM_LINTER_GUIDE.md](docs/LLM_LINTER_GUIDE.md):** The exhaustive Burn List of banned syntax, AST traps, and CI/CD bypass protocols.

## API Contracts
You MUST use the documentation in docs/modules/ as your strict API contract:
* docs/modules/user_websites.md: Proxy Ownership and slug routing.
* docs/modules/manual_library.md: Knowledge base injection.
* docs/modules/compliance.md: GDPR cookie bars and legal pages.

---

## Setup commands

**1. Odoo Test Server & Database Rebuild**
To rebuild the database, lint the code, and run Odoo unit tests:
./tools/START.sh user_websites

---

## Testing instructions

Before submitting any code, it MUST pass the following active linters:

**1. The Burn List Linter**
Scans for deprecated Odoo syntax and security anti-patterns (See LLM Linter Guide).
python3 tools/check_burn_list.py .

**2. Dependency Pre-Flight**
Validates that all modules listed in manifest files exist in the environment.
python3 tools/pre_flight_check.py -m <path_to_module> --addons-path <paths>

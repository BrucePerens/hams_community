# AGENTS.md

This document configures the behavior, context, and boundaries for any Large Language Model (LLM), AI IDE (Cursor, Windsurf, Copilot), or CLI agent interacting with this repository.

---

## Persona & Boundaries

* **Persona:** You are an expert AI developer assistant operating in a strict, **zero-guessing** environment.
* **Zero-Guessing Policy:** Strict prohibition against AI hallucination of database states, file structures, or Odoo APIs. If you do not know a path or signature with 100% certainty, you MUST stop and ask.
* **Anti-Evasion Policy (No Linter Dodging):** You are STRICTLY FORBIDDEN from using semantic tricks (e.g., `csrf=not True`), string decoupling (e.g., `'.su' + 'do()'`), or splitting UI-crashing tags to silently evade regex-based linter detection. If a rule triggers, fix the underlying architecture.
* **The Exactness Guarantee (Patch Protocol):** For files exceeding 100 lines, you may output targeted Unified Diffs or search-and-replace blocks. However, the provided blocks MUST be syntactically whole. You are STRICTLY FORBIDDEN from using placeholders (e.g., `// ... rest of method`) inside the modified code.
* **Tone:** Direct, professional, and technical. Do not praise the user. Do not announce basic compliance with formatting rules.

---

## Project overview

**Open Source Community Odoo Modules**
This repository contains open-source modules designed for **Odoo 19 Community** under the AGPL-3.0 license. It provides decentralized user websites, global privacy compliance, and clean-room hierarchical manual libraries.

---

## Output Format & Transport (CRITICAL)

When generating or modifying code, you **MUST** output your response using the **AEF 4.0 JSON** schema inside a single ```json code block.
1. **Asymmetric Transport Mandate:** You MUST NEVER output Base64. Your generated `content` field MUST be a JSON array of strings (one string per line, ending with `\n`).
2. **UI Crash Prevention:** If your file contains literal HTML/XML tags that might crash a markdown renderer, you MUST URL-encode the strings in the array and specify `"encoding": "url-encoded"`. Otherwise, specify `"encoding": "utf-8"`.
3. **Protocol Completeness (Finish the Job):** If you introduce new schema changes, you MUST ensure the extraction scripts are updated.
4. **Multi-Step Disclosure:** If your response is part of a multi-step process, clearly state the required successive steps in plain text *before* rendering the JSON block.

---

## Code style & Architecture

Before writing any code, you MUST read and adhere to the following mandates:

1. **[LLM_GENERAL_REQUIREMENTS.md](docs/LLM_GENERAL_REQUIREMENTS.md):** Universal operational protocols, WCAG 2.1 AA compliance, GDPR erasure, and Proxy Ownership security patterns.
2. **[LLM_ODOO_REQUIREMENTS.md](docs/LLM_ODOO_REQUIREMENTS.md):** Odoo 19+ specific constraints. Contains **The Burn List** (anti-patterns and legacy syntax to avoid).

## API Contracts
You MUST use the documentation in `docs/modules/` as your strict API contract:
* `docs/modules/user_websites.md`: Proxy Ownership and slug routing.
* `docs/modules/manual_library.md`: Knowledge base injection.
* `docs/modules/compliance.md`: GDPR cookie bars and legal pages.

---

## Setup commands

**1. Odoo Test Server & Database Rebuild**
To rebuild the database, lint the code, and run Odoo unit tests:
```bash
./tools/START.sh user_websites
```

---

## Testing instructions

Before submitting any code, it MUST pass the following active linters:

**1. The Burn List Linter**
Scans for deprecated Odoo syntax and security anti-patterns.
```bash
python3 tools/check_burn_list.py .
```

**2. Dependency Pre-Flight**
Validates that all modules listed in `__manifest__.py` exist in the environment.
```bash
python3 tools/pre_flight_check.py -m <path_to_module> --addons-path <paths>
```

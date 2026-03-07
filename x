@@BOUNDARY_DOCS_UPDATE@@
Path: docs/LLM_LINTER_GUIDE.md
Operation: search-and-replace

<<<< SEARCH
| Sudo Override | `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]` | Exclusively for `database.secret` extraction. |
| Test Commit | `# burn-ignore-test-commit` | Exclusively for `RealTransactionCase` where real DB commits are required to test ORM caches. |

---

## 7. ⚓ Semantic Anchors & UI Tour Mandate
====
| Sudo Override | `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]` | Exclusively for `database.secret` extraction. |
| Test Commit | `# burn-ignore-test-commit` | Exclusively for `RealTransactionCase` where real DB commits are required to test ORM caches. |

### 🚨 Critical Formatting & Placement Rules for Bypasses
1. **The Python Formatter (`# fmt: skip`) Trap:** The Black code formatter will wrap long lines (like dictionaries, lists, or long method signatures) and detach your inline linter comments, causing the AST linter to fail. **Whenever you apply an `# audit-ignore-*` or `# burn-ignore` comment to a multi-line structure, you MUST append `  # fmt: skip` to the exact same line.** This mathematically locks the bypass tag to the correct AST node.
2. **The Dual XML Anchor Placement:** To satisfy both the XML architecture linter (`check_burn_list.py`) and the bidirectional traceability linter (`verify_anchors.py`) simultaneously, you MUST use the following dual-comment structure:
   * The traceability anchor `` MUST be placed immediately **above** the `<record>` or `<template>` tag.
   * The burn list bypass `` MUST be placed immediately **inside** the `<record>` or `<template>` tag (on the exact same line as the opening bracket).

---

## 7. ⚓ Semantic Anchors & UI Tour Mandate
>>>> REPLACE

@@BOUNDARY_DOCS_UPDATE@@
Path: docs/LLM_EXPERIENCE.md
Operation: overwrite

# LLM Experience & Hard-Learned Lessons

*This document serves as a persistent memory bank for the Large Language Model (LLM) across sessions. It is a place to record critical experiences, edge-cases, and hard-learned lessons that the LLM should not forget between sessions. The LLM is free to choose what to append and document here.*

---

## 1. The Web UI Markdown Renderer Trap (XML Data Loss)
**The Trap:** The conversational Web UI aggressively parses and strips out HTML/XML comments (``) from plaintext markdown blocks *before* the Python extraction script (`parcel_extract.py`) ever receives the payload. This leads to silent data loss, specifically destroying mandatory `[%ANCHOR: ...]` and `audit-ignore-*` tags in XML files.
**The Solution:** When patching or overwriting XML files, the LLM **MUST ALWAYS** use `Encoding: url-encoded` in the Parcel header and percent-encode the angle brackets (`<` becomes `%3C`, `>` becomes `%3E`) and percent signs (`%` becomes `%25`).

## 2. The Python Formatter (Black) vs. AST Linter Trap
**The Trap:** The project uses the Black code formatter. When returning dictionaries, lists, or multi-line structures in Python (like JSON-RPC responses), Black will reformat them across multiple lines. This detaches inline `# audit-ignore-*` or `# burn-ignore` comments from the specific AST node they were meant to protect, causing CI/CD pipeline failures.
**The Solution:** Whenever applying a linter bypass comment to a multi-line Python structure, the LLM **MUST** append `  # fmt: skip` to the end of the comment (e.g., `return {"error": "..."}  # audit-ignore-i18n: Tested by [%ANCHOR: test_name]  # fmt: skip`).

## 3. The Dual XML Anchor Strictness
**The Trap:** The platform utilizes two separate linters with conflicting structural requirements for XML records. `verify_anchors.py` requires traceability anchors to be easily found, while `check_burn_list.py` requires the bypass tag to be embedded directly within the node's AST.
**The Solution:** XML records and templates require a specific dual-comment structure:
```xml
<record id="my_id" model="ir.ui.view"> ...
</record>
```

## 4. Extraction Engine Resiliency
**Experience:** The `parcel_extract.py` script was upgraded to catch `IndentationError` and `SyntaxError` from the Python `tokenize` engine. It now gracefully degrades to a whitespace-agnostic replacement algorithm that perfectly preserves relative indentation. Partial, unbalanced Python snippets can now be safely used in `search-and-replace` blocks without crashing the tokenizer.

@@BOUNDARY_DOCS_UPDATE@@--

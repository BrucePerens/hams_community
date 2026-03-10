# LLM Experience & Hard-Learned Lessons

*This document serves as a persistent memory bank for the Large Language Model (LLM) across sessions. It is a place to record critical experiences, edge-cases, and hard-learned lessons that the LLM should not forget between sessions. The LLM is free to choose what to append and document here.*

## 1. The Web UI Markdown Renderer Trap (XML Data Loss)

**The Trap:** The conversational Web UI aggressively parses and strips out HTML/XML comments (`<!-- ... -->`) from plaintext markdown blocks *before* the Python extraction script (`parcel_extract.py`) ever receives the payload. This leads to silent data loss, specifically destroying mandatory `[%ANCHOR: ...]` and `audit-ignore-*` tags. It also silently destroys `<<<< SEARCH` blocks if the search target contains an HTML comment.
**The Solution:** When your payload (overwrite OR search-and-replace block) contains HTML/XML comments, the LLM **MUST ALWAYS** use `Encoding: url-encoded` in the Parcel header and percent-encode the angle brackets (`<` becomes `%3C`, `>` becomes `%3E`) and percent signs (`%` becomes `%25`). This applies to *any* file type being modified, including Markdown documentation that contains HTML comment examples.

## 2. The Python Formatter (Black) vs. AST Linter Trap

**The Trap:** The project uses the Black code formatter. When returning dictionaries, lists, or multi-line structures in Python (like JSON-RPC responses), Black will reformat them across multiple lines. This detaches inline `# audit-ignore-*` or `# burn-ignore` comments from the specific AST node they were meant to protect, causing CI/CD pipeline failures.
**The Solution:** Whenever applying a linter bypass comment to a multi-line Python structure, the LLM **MUST** append `  # fmt: skip` to the end of the comment (e.g., `return {"error": "..."}  # audit-ignore-i18n: Tested by [%ANCHOR: example_test_name]  # fmt: skip`).

## 3. The Dual XML Anchor Strictness

**The Trap:** The platform utilizes two separate linters with conflicting structural requirements for XML records. `verify_anchors.py` requires traceability anchors to be easily found, while `check_burn_list.py` requires the bypass tag to be embedded directly within the node's AST.
**The Solution:** XML records and templates require a specific dual-comment structure:

```xml
<!-- Verified by [%ANCHOR: example_test_name] -->
<record id="my_id" model="ir.ui.view"> <!-- audit-ignore-view: Tested by [%ANCHOR: example_test_name] -->
    ...
</record>
```

## 4. Extraction Engine Resiliency

**Experience:** The `parcel_extract.py` script was upgraded to catch `IndentationError` and `SyntaxError` from the Python `tokenize` engine. It now gracefully degrades to a whitespace-agnostic replacement algorithm that perfectly preserves relative indentation. Partial, unbalanced Python snippets can now be safely used in `search-and-replace` blocks without crashing the tokenizer.

## 5. The Four-Backtick Wrapper Trap & Inline Escaping

**The Trap:** LLMs naturally default to using three backticks for plaintext code blocks. If a generated payload (especially when patching documentation) contains its own nested three-backtick code block, it prematurely terminates the Markdown parser, completely destroying the extraction boundary.
**The Solution:** The outermost Parcel block MUST ALWAYS be wrapped in at least four (or preferably five) backticks.

## 6. The AST "Dead Code" Evasion Trap

**The Trap:** When bypassing linters with `audit-ignore-*`, the LLM must write an automated test. Previously, LLMs might place the required assertion (like `get_view`) inside a `for` loop or after a `return` statement to technically satisfy the text matcher. The deep AST linter (`check_burn_list.py`) physically evaluates the execution path and will instantly fail the build if the assertion is in unreachable code or wrapped in a loop.
**The Solution:** Required test assertions must be genuine, sequentially executed statements in the top-level block of the test function.

## 7. The RPC Mass Assignment Trap

**The Trap:** Passing `kwargs` directly into `.create(**kwargs)` or `.write(kwargs)` inside controller routes triggers a strict AST RPC Mass Assignment block. This prevents attackers from submitting extraneous form fields that overwrite secure database columns.
**The Solution:** The LLM must always explicitly map and whitelist allowed fields into a new dictionary before passing it to ORM mutation methods.

## 8. The Formatting Drift & AST Fallback Trap

**The Trap:** When using `search-and-replace` on Python files that have been heavily formatted by `black` (especially long arrays, dictionaries, and chained methods), the semantic token matcher often fails because line breaks and trailing commas don't align with the LLM's generated search block.
**The Solution:** For files under 500 lines, strictly utilize the `overwrite` operation to bypass diffing friction entirely. For files over 500 lines, provide 2-3 lines of surrounding context in your `<<<< SEARCH` block. The integrated Fuzzy Line-Matching fallback (`difflib.SequenceMatcher`) will absorb indentation and formatting drift, allowing you to safely replace partial code fragments without breaking the AST parser.

## 9. Bidirectional Anchor Strictness for Linter Bypasses

**The Trap:** When adding an `audit-ignore-*` tag with a "Tested by" anchor (e.g., `# audit-ignore-i18n: Tested by [%ANCHOR: example_test_my_feature]`), simply placing `# Tests [%ANCHOR: example_test_my_feature]` in the test file is insufficient and will trigger an ADR-0054 CI/CD failure because the linter interprets it as an orphaned source anchor.
**The Solution:** The LLM must ensure the base source anchor is fully declared and linked. The source code must define the base anchor (`# [%ANCHOR: example_my_feature]`), the bypass must reference the test (`Tested by [%ANCHOR: example_test_my_feature]`), and the test file must reference both the source (`# Tests [%ANCHOR: example_my_feature]`) and define its own anchor (`# [%ANCHOR: example_test_my_feature]`).

## 10. The Obsolete `burn-ignore-test-commit` Trap

**The Trap:** The linter (`check_burn_list.py`) was structurally updated to natively allow `self.env.cr.commit()` and `self.env.cr.rollback()` exclusively within tests that inherit from `RealTransactionCase`. Because of this native AST awareness, the legacy `# burn-ignore-test-commit` bypass tag is now obsolete. If left in the code, the linter will strictly fail the build with an "UNAUTHORIZED BYPASS" error.
**The Solution:** When porting or updating older repositories or tests that use `test_real_transaction`, you MUST remove any instances of `# burn-ignore-test-commit  # fmt: skip` attached to commits. Simply use `self.env.cr.commit()`.

## 11. The E741 Ambiguous Variable Trap & Extractor Partial Updates

**The Trap:** Using single-letter variables like `l`, `O`, or `I` (especially in list comprehensions) triggers a strict `flake8` E741 violation because they are visually indistinguishable from numbers or other letters in many fonts. This instantly fails the fast-fail CI/CD pipeline. Additionally, attempting to patch the `tools/parcel_extract.py` file with `search-and-replace` often leaves orphaned variables and broken logic due to the Meta-Tooling Exception.
**The Solution:** Never use `l`, `O`, or `I` as variables; always use descriptive names like `line_item`, `chunk`, or `rec`. Furthermore, always respect the Meta-Tooling Exception and use the `overwrite` operation when updating `parcel_extract.py` to prevent catastrophic script corruption.

## 12. The Conversational Canvas Trigger (Nuanced 3-Line Rule)

**The Trap:** The system instructions possess competing directives regarding response length. One explicitly mandates routing *anything* over 3 lines (especially analyses and explanations) into the Canvas/Document workflow. Conversely, another instruction expects standard conversational chat for Q&A, explanations, and clarifications. Sticking too rigidly to the "3-line rule" for conversational explanations forces the UI to parse plain text into a document with bizarre, auto-generated filenames, breaking the user experience.
**The Solution:** The LLM MUST balance the 3-line rule with contextual intent. For formal reports, code files, or structured documentation meant to be exported or edited, ALWAYS use the file generation workflow (Parcel). For interactive Q&A, clarifications, or confirming system rules with the developer, respond conversationally directly in the chat window, even if it slightly exceeds 3 lines, to prevent triggering an unwanted Canvas window.

## 13. The Markdown Panel / Canvas Copy-Paste Trap

**The Trap:** System prompts might instruct the LLM to use UI panels, "Canvas", or standard markdown code blocks to generate `.md` files. However, the web UI's "copy contents" function for Markdown panels often fails to copy the raw, unformatted markdown correctly (stripping characters or improperly rendering them), breaking the `parcel_extract.py` workflow if the user attempts to copy it to their local machine.
**The Solution:** The LLM MUST NEVER use standard UI panels or Canvas features to output Markdown files. All Markdown file modifications and generations MUST be delivered exclusively via the MIME-like Parcel transport schema (`@@BOUNDARY_...@@` inside a 4-backtick `plaintext` block), using the `Encoding: url-encoded` header if HTML/XML comments or problematic angle brackets are present.

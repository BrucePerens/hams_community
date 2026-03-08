# LLM Experience & Hard-Learned Lessons

*This document serves as a persistent memory bank for the Large Language Model (LLM) across sessions. It is a place to record critical experiences, edge-cases, and hard-learned lessons that the LLM should not forget between sessions. The LLM is free to choose what to append and document here.*

---

## 1. The Web UI Markdown Renderer Trap (XML Data Loss)
**The Trap:** The conversational Web UI aggressively parses and strips out HTML/XML comments (`<!-- ... -->`) from plaintext markdown blocks *before* the Python extraction script (`parcel_extract.py`) ever receives the payload. This leads to silent data loss, specifically destroying mandatory `[%ANCHOR: ...]` and `audit-ignore-*` tags in XML files.
**The Solution:** When patching or overwriting XML files, the LLM **MUST ALWAYS** use `Encoding: url-encoded` in the Parcel header and percent-encode the angle brackets (`<` becomes `%3C`, `>` becomes `%3E`) and percent signs (`%` becomes `%25`).

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

## 5. The Four-Backtick Wrapper Trap
**The Trap:** LLMs naturally default to using three backticks for plaintext code blocks. If a generated payload (especially when patching `README.md` or other documentation) contains its own nested three-backtick code block, it prematurely terminates the Markdown parser, completely destroying the extraction boundary.
**The Solution:** The outermost Parcel block MUST ALWAYS be wrapped in at least four backticks (````plaintext ... ````).

## 6. The AST "Dead Code" Evasion Trap
**The Trap:** When bypassing linters with `audit-ignore-*`, the LLM must write an automated test. Previously, LLMs might place the required assertion (like `get_view`) inside a `for` loop or after a `return` statement to technically satisfy the text matcher. The deep AST linter (`check_burn_list.py`) physically evaluates the execution path and will instantly fail the build if the assertion is in unreachable code or wrapped in a loop.
**The Solution:** Required test assertions must be genuine, sequentially executed statements in the top-level block of the test function.

## 7. The RPC Mass Assignment Trap
**The Trap:** Passing `kwargs` directly into `.create(**kwargs)` or `.write(kwargs)` inside controller routes triggers a strict AST RPC Mass Assignment block. This prevents attackers from submitting extraneous form fields that overwrite secure database columns.
**The Solution:** The LLM must always explicitly map and whitelist allowed fields into a new dictionary before passing it to ORM mutation methods.

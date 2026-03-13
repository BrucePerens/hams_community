# LLM Experience & Hard-Learned Lessons

*This document serves as a persistent memory bank for the Large Language Model (LLM) across sessions. It is a place to record critical experiences, edge-cases, and hard-learned lessons that the LLM should not forget between sessions. The LLM is free to choose what to append and document here.*

## 1. The Web UI Markdown Renderer Trap (XML Data Loss)
**The Trap:** The conversational Web UI aggressively parses and strips out HTML/XML comments (`<!-- ... -->`) from plaintext markdown blocks *before* the Python extraction script ever receives the payload.
**The Solution:** When your payload contains HTML/XML comments, you **MUST ALWAYS** use `Encoding: url-encoded` in the Parcel header and percent-encode the angle brackets and percent signs.

## 2. The Python Formatter (Black) vs. AST Linter Trap
**The Trap:** The Black formatter will wrap multi-line structures, detaching inline `# audit-ignore-*` comments from the AST node they protect.
**The Solution:** Append `  # fmt: skip` to the end of any linter bypass comment applied to multi-line Python structures.

## 3. The XML Line-Wrapping AST Trap (Nested Anchors)
**The Trap:** Placing anchors inline with `<record>` tags causes AST tracking to fail when formatters wrap the line.
**The Solution:** Always nest both the `[%ANCHOR]` and the `audit-ignore-view` comments directly **inside** the `<record>` or `<template>` tags as child nodes.

## 4. Extraction Engine Resiliency
**Experience:** The extraction script gracefully degrades to whitespace-agnostic and fuzzy-line matching algorithms. Partial, unbalanced Python snippets can be safely used in `search-and-replace` blocks without crashing the tokenizer.

## 5. The Four-Backtick Wrapper Trap
**The Trap:** Using three backticks for the outer Parcel block fails if the payload contains its own three-backtick markdown blocks.
**The Solution:** The outermost Parcel block MUST ALWAYS be wrapped in at least four (preferably five) backticks.

## 6. The AST "Dead Code" Evasion Trap
**The Trap:** Placing required test assertions inside `for` loops, `if False:` blocks, or after `return` statements to trick the text-matcher will instantly fail the AST physical execution path check.
**The Solution:** Required test assertions must be genuine, sequentially executed statements.

## 7. The RPC Mass Assignment Trap
**The Trap:** Passing `kwargs` directly into `.create(**kwargs)` in controller routes triggers an AST security block.
**The Solution:** Explicitly map and whitelist allowed fields into a new dictionary.

## 8. The Formatting Drift & AST Fallback Trap
**The Solution:** For files under 500 lines, strictly utilize the `overwrite` operation. For larger files, provide 2-3 lines of surrounding context to leverage the Fuzzy Line-Matching fallback.

## 9. Bidirectional Anchor Strictness
**The Trap:** Adding an `audit-ignore` tag without fully linking the base source anchor, the bypass link, and the test file link triggers a bidirectional violation.
**The Solution:** Ensure the tripartite linkage is complete (Source Definition -> Bypass Citation -> Test Definition + Source Citation).

## 10. The Obsolete `burn-ignore-test-commit` Trap
**The Trap:** The linter natively allows `env.cr.commit()` inside `RealTransactionCase`. Using the legacy `# burn-ignore-test-commit` tag is now an unauthorized bypass.
**The Solution:** Remove legacy commit bypass tags.

## 11. The E741 Ambiguous Variable Trap & Extractor Partial Updates
**The Trap:** Using single-letter variables like `l`, `O`, or `I` triggers a `flake8` E741 violation.
**The Solution:** Use descriptive names like `line_item`, `chunk`, or `rec`.

## 12. The Markdown Panel / Canvas Copy-Paste Trap
**The Trap:** The web UI's Canvas "copy contents" function strips and destroys raw markdown formatting.
**The Solution:** Deliver all markdown modifications exclusively via the MIME-like Parcel transport schema.

## 13. The Global URL-Encoding Token Bloat Trap
**The Trap:** Applying `Encoding: url-encoded` to standard Markdown files encodes every single space into `%20`, massively bloating the payload and triggering token-limit Canvas crashes.
**The Solution:** ONLY use `Encoding: url-encoded` on payloads that physically contain HTML/XML comments. For pure Markdown or Python files, use standard unencoded text inside a 5-backtick wrapper.

## 14. The System Package `.venv` Bridge Trap
**The Trap:** Odoo is an OS-level package (`apt`). Executing it via standard shell commands ignores the local Python `.venv` where external daemon packages (like `pika`) are installed. Conversely, trying to `pip install odoo` locally triggers a nightmare of C-extension compilations.
**The Solution:** Set `export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"` in the execution shell to bridge the OS-level Odoo framework into the isolated `.venv`, and explicitly execute `"$VENV_PYTHON" /usr/bin/odoo`.

## 15. The Upstream Core Test Suite Trap
**The Trap:** Running test scripts with target module `all` forces Odoo to test its own core framework, which fails on local development machines missing specific system binaries (like `wkhtmltopdf` or exact MIME setups).
**The Solution:** Dynamically scan the workspace for custom modules (`find . -name "__manifest__.py"`) and exclusively target those modules via the `-i` and `-u` execution flags.

## 16. The View Bypass Duplicate Anchor Trap
**The Trap:** Injecting `<!-- [%ANCHOR: my_test] -->` into an XML view alongside `<!-- audit-ignore-view: Tested by [%ANCHOR: my_test] -->` causes the linter to throw a Duplicate Anchor error if the Python test file also defines the anchor.
**The Solution:** For Linter bypasses in views, ONLY include the `audit-ignore-view: Tested by ...` tag. Do not redefine the base anchor in the view unless the view itself is the primary architectural source of the feature.

# ADR 0053: XPath Rendering Verification Mandate

## Status
Accepted

## Context
During the transition to Odoo 19, we discovered a major architectural trap regarding XML injections.
An `<xpath>` statement that successfully parses during database initialization only proves that the *target node exists* in the parent view.
It **does not** guarantee that the injected QWeb or HTML actually renders in the browser DOM.
The parent view might discard it, or the wrapping elements might be structurally incompatible, leading to a silent UI failure that standard test runners will not catch.

## Decision
All `<xpath>` injections MUST be explicitly and physically tested to verify successful rendering.
1. **Linter Enforcement:** The `check_burn_list.py` linter will globally flag any `<xpath>` element as an `[AUDIT]` warning.
2. **The Bypass Comment:** Developers must explicitly bypass this warning by placing `` on the same line as the `<xpath>` declaration.
3. **Physical Rendering Tests:** The cross-referenced Semantic Anchor MUST point to an automated unit test.
This test must execute `get_view()` (for backend forms) or HTTP `url_open()` / `_get_combined_arch()` (for frontend QWeb templates) and physically assert the presence of the injected text or HTML payload in the compiled architecture.

## Consequences
* **Positive:** Mathematically guarantees that UI customizations, settings blocks, and website widgets are actually visible to the user.
Prevents silent UI failures from escaping into production during Odoo version upgrades.
* **Negative:** Increases testing boilerplate, requiring developers to fetch compiled string architectures or mock HTTP sessions for simple view extensions.

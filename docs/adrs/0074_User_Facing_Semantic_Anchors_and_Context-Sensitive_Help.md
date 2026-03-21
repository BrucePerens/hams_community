# ADR 0074: User-Facing Semantic Anchors & Context-Sensitive Help

## Status
Accepted

## Context
To ensure platform usability, we must guarantee that every interactive feature (buttons, forms, frontend controllers) is properly documented for the end-user. The platform enforces traceability via Semantic Anchors (`[@ANCHOR: example_feature_name]`), but injecting raw anchor strings into polished user manuals (`data/documentation.html`) creates confusing "cybercrud" that violates our UX standards.

Previously, we considered hiding these anchors inside HTML comments (``). [cite_start]However, our operational experience revealed a critical vulnerability: web-based LLM chat interfaces aggressively strip HTML comments from code blocks during generation (The Web UI Markdown Renderer Trap)[cite: 1512]. This causes silent data loss and destroys the traceability matrix when AI agents patch documentation.

Furthermore, we want to provide users with immediate assistance directly within the UI, rather than forcing them to read a dense manual to find answers.

## Decision
We mandate a specialized anchor protocol for all user-facing features, utilizing standard HTML5 attributes to achieve invisible traceability and context-sensitive help simultaneously.

### 1. The `UX_` Prefix Convention
Any Semantic Anchor representing a user-facing interaction (a frontend controller, a QWeb view, or an interactive button) MUST be prefixed with `UX_`. 
* *Example:* `[@ANCHOR: UX_REPORT_VIOLATION]`

### 2. HTML5 Traceability (Zero UI Pollution)
Inside the end-user manual (`data/documentation.html`), the documentation for a feature MUST be anchored using a combination of the `id` and `data-trace` attributes on the relevant HTML tag (e.g., a heading or paragraph).
* *Example:* `<h3 id="UX_REPORT_VIOLATION" data-trace="[@ANCHOR: UX_REPORT_VIOLATION]">Reporting Content</h3>`
* [cite_start]This hides the raw syntax from the user, satisfies the `verify_anchors.py` CI/CD regex parser, and completely bypasses the LLM comment-stripping trap [cite: 1512] because standard DOM attributes are preserved during Markdown generation.

### 3. Context-Sensitive Help
Frontend QWeb templates MUST leverage these `id` tags by injecting discrete help icons (e.g., `(?)` or a FontAwesome question circle) next to complex UI elements. 
* These links must point directly to the manual's URL fragment: `href="/user-websites/documentation#UX_REPORT_VIOLATION"`.
* This allows the browser to instantly snap the user's viewport to the exact paragraph explaining the feature they are currently looking at.

### 4. Strict CI/CD Enforcement
The `verify_anchors.py` pipeline is updated to explicitly extract all `UX_` prefixed anchors from the codebase and perform a strict set difference against the anchors found in `data/documentation.html` files. If a user-facing feature is coded but not documented, the build mathematically fails.

## Consequences
* **Mathematical Completeness:** We can programmatically guarantee 100% documentation coverage for all user-facing features.
* **Enhanced User Experience:** Operators receive immediate, context-aware assistance directly inside the application.
* [cite_start]**AI Resilience:** The traceability matrix is permanently immunized against Markdown parser data loss during LLM code generation[cite: 1512].

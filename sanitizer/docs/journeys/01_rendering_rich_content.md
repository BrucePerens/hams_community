# User Journey: Rendering Rich Content

## Phase 1: Global Configuration
*(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: patch_lxml_cleaner])*
Upon module installation, the system automatically patches the low-level HTML cleaning utility. This ensures that even before Odoo-specific filters are applied, the core library is instructed not to strip out critical tags like `<iframe>` or `<script>`.

## Phase 2: Safelist Expansion
*(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: expand_tag_safelist])*
*(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: expand_attribute_safelist])*
The platform then updates Odoo's internal safelists. This allows high-level components, such as the mail module and web editor, to recognize and accept these tags and their associated attributes (e.g., `allowfullscreen`, `data-bs-toggle`) as safe for storage and display.

## Phase 3: Content Authoring and Display
A user creates a new record containing an embedded interactive map using an `<iframe>`. Because of the overrides, the map is preserved exactly as intended when the record is saved. When another user views the record, the browser correctly renders the embedded content, providing a rich, interactive experience that would have otherwise been sanitized away.

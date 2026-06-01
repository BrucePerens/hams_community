# Ham Sanitizer Override

This module provides a global override for Odoo's HTML sanitization engine. It authorizes specific tags and attributes that are otherwise stripped for security reasons, enabling more flexible content rendering.

## Functionality

By installing this module, the following changes are applied globally to Odoo's HTML sanitization:

- **Authorized Tags**: `<script>`, `<iframe>`, and `<dfn>` are added to the list of allowed tags.
- **Authorized Attributes**: The following attributes are added to the global allowlist:
    - `src`: Essential for external scripts and iframe content.
    - `allowfullscreen`: Enables full-screen mode for embedded videos.
    - `frameborder`: Controls the border around iframes (legacy but still used).
    - `allow`: Modern attribute for iframe feature policy (e.g., microphone, camera).
    - `type`: Required for specifying script types (e.g., `text/javascript`, `module`).
    - `async`: Allows scripts to be loaded asynchronously.
    - `defer`: Allows scripts to be executed after the document has been parsed.
    - `charset`: Specifies the character encoding for external scripts.
    - `crossorigin`: Manages CORS requests for external assets.
    - `data-bs-toggle`: Enables Bootstrap interactive components (tabs, tooltips, etc.).
- **Cleaner Patch**: Patches the underlying `lxml_html_clean.Cleaner` to ensure that even if Odoo's high-level sanitizer is bypassed, the low-level cleaner does not aggressively strip scripts and frames.

## Usage

1. **Install the module**: The overrides are applied immediately upon loading.
2. **Embed Content**: You can now paste HTML containing `<script>` or `<iframe>` into Odoo HTML fields (e.g., Blog Posts, Forum, Website Pages).
3. **Bootstrap Components**: Use `data-bs-toggle` in your HTML to trigger Bootstrap JavaScript behaviors without them being stripped.

## Security Considerations

**CRITICAL VULNERABILITY WARNING**:
Authorizing `<script>` and `<iframe>` tags globally significantly increases the risk of **Cross-Site Scripting (XSS)** attacks.

- **Risk**: Any user with permission to edit an HTML field can inject malicious JavaScript that executes in the context of other users' browsers, potentially stealing session cookies or performing actions on their behalf.
- **Mitigation**:
    - Only use this module in private, trusted environments.
    - Ensure all users with "Editor" or "Designer" permissions are fully vetted.
    - This module implements a "Fail Fast" protocol: it will forcefully crash the Odoo process if Odoo's internal `mail` tools change in a way that makes these patches unsafe or ineffective.

## Multi-Tenant Awareness

**Architectural Note: Global Scope**
This module is explicitly designed as a **Global Module** and is NOT multi-tenant or multi-website aware.

**Reasoning**:
HTML sanitization rules in Odoo are implemented via global variables in the `odoo.tools.mail` module and by patching the `lxml_html_clean.Cleaner` class. These components are shared across the entire Odoo process. Implementing per-tenant sanitization would require a significantly more complex architecture that intercepts every sanitization call to inject tenant-specific context, which is currently outside the scope of this core override. Consequently, once this module is installed, the relaxed security rules apply to ALL companies and ALL websites hosted on the instance.

## Implementation Details

- **Monkey-patching `lxml_html_clean.Cleaner`**: We override the `__init__` method of the base `Cleaner` class. This ensures that any instance created (including Odoo's internal `_Cleaner` subclass) has `scripts`, `frames`, and `embedded` set to `False`, preventing them from being stripped at the low level.
- **Odoo Safelist Expansion**: We modify `mail.SANITIZE_TAGS` and `mail.safe_attrs` during the `post_load` hook. This ensures the changes are applied after the `mail` module is fully loaded but before the server starts processing requests.

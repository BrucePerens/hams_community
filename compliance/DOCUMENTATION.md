# Site Owner's Guide to Regulatory Compliance

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Module Name:** `compliance`
**Version:** Odoo 19 Community
**Summary:** A comprehensive guide for community administrators regarding GDPR, CCPA, ePrivacy, WCAG, and platform moderation regulations, and how this platform automatically handles them.

---

## 1. Data Privacy & Protection (GDPR & CCPA)

Modern data protection laws like the General Data Protection Regulation (GDPR) in Europe and the California Consumer Privacy Act (CCPA) mandate strict handling of personal data. This platform is built from the ground up with **Privacy by Design**.

* **Data Minimization:** The platform actively avoids unnecessary data collection. System view counters (such as page hits or blog views) operate on the server side without logging Personally Identifiable Information (PII) or IP addresses.
* **Data Portability (Right to Access):** Users have the legal right to request a copy of their data. The platform provides an automated JSON export tool at the `/my/privacy` portal dashboard, allowing users to download their authored content instantly.
* **Right to Erasure (Right to be Forgotten):** Users must be able to delete their accounts and data. An automated hard-delete facility is available at `/my/privacy`, which immediately unlinks all authored pages and blogs, and removes the user from public directories.

---

## 2. Cookie Consent (ePrivacy Directive)

The ePrivacy Directive (often referred to as the "Cookie Law") requires explicit user consent before storing non-essential cookies (such as analytics, tracking, or marketing cookies) on a user's device.

* **Native Integration:** The `compliance` module automatically enforces Odoo's native Cookie Consent Bar across all active websites in your database upon installation.
* **Compliance Protocol:** Site owners must not bypass this bar by hardcoding third-party tracking scripts (like Google Analytics or Meta Pixels) directly into website templates. All trackers must hook into the core framework's consent state so they are blocked until the user explicitly clicks "Accept".

---

## 3. Web Accessibility (WCAG 2.1 AA)

The Web Content Accessibility Guidelines (WCAG) ensure that web content is accessible to people with disabilities, including visual, auditory, physical, speech, cognitive, and neurological disabilities. Many jurisdictions now legally require WCAG 2.1 AA compliance for public-facing websites.

* **Semantic HTML:** The platform templates mandate proper tag hierarchy (e.g., using proper `<h1>` to `<h6>` structures and `<button>` tags instead of styled `<div>` elements) to ensure screen readers can accurately interpret the page.
* **Keyboard Navigability:** All interactive elements, including moderation modals and table of contents sidebars, are fully navigable via the `Tab` key with visible focus states.
* **ARIA Labels:** Icon-only buttons (like the Report Violation flag or UI toggles) are equipped with `aria-label` attributes to describe their function to assistive technologies.

---

## 4. Platform Moderation (Digital Services Act / DSA)

Regulations governing user-generated content, such as the EU's Digital Services Act (DSA), require platforms to have transparent, accessible, and fair moderation processes.

* **Notice and Action Mechanism:** The platform features a persistent "Report Violation" button on all user-generated content, allowing guests and logged-in users to easily report abuse.
* **Reporter Shielding:** To prevent retaliation and protect user privacy, the identity of the complainant is strictly shielded from the content owner via ORM Record Rules. It is only visible to platform administrators.
* **Fair Appeals:** The platform utilizes an automated Three-Strike suspension system. This is paired with a built-in appeals process, ensuring suspended users have a mechanism to contest moderation decisions.

---

## 5. Required Legal Boilerplates

To operate legally, your website must publicly display specific policy documents. The `compliance` module automatically provisions editable, AGPL-3 compatible templates for these required pages:

* **Privacy Policy** (`/privacy`)
* **Cookie Policy** (`/cookie-policy`)
* **Terms of Service** (`/terms`)

**Non-Destructive Updates:** These pages are provisioned using non-destructive `noupdate="1"` XML. This ensures that any manual edits you make to these policies using the Odoo website builder will never be overwritten during future module upgrades or server restarts.

---

## 6. Module Compliance Statement: Global Compliance

**How the `compliance` module complies with the above regulations:**

* **ePrivacy:** Directly enforces the activation of the core `cookies_bar` upon installation via the `post_init_hook`.
* **Transparency:** Automatically provisions the required legal boilerplate pages (Privacy Policy, Cookie Policy, Terms of Service) utilizing standard Odoo website pages.
* **WCAG:** The generated QWeb templates for the legal pages utilize semantic HTML structures and respect standard theme contrasts.
* **Documentation Integration:** Installs this exact guide directly into the `knowledge.article` API so administrators can reference it without leaving the Odoo backend.


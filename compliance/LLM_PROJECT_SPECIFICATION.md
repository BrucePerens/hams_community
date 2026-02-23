# LLM PROJECT SPECIFICATION: GLOBAL COMPLIANCE (`compliance`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Inheritance:** This specification strictly inherits and enforces all operational mandates, technical standards, and output formatting rules defined in `LLM_GENERAL_REQUIREMENTS.md` and `LLM_ODOO_REQUIREMENTS.md`.

---

## 1. PROJECT OVERVIEW & FUNCTIONAL MANDATE

**Module Name:** `compliance`
**Summary:** The central hub for automated regulatory compliance (GDPR, CCPA, ePrivacy) across the platform.
**Objective:** To ensure the platform meets global privacy and transparency standards automatically upon installation, with a "do no harm" approach to existing configurations.

---

## 2. FEATURE SPECIFICATIONS

### A. Automated Cookie Consent Enforcement
* **Requirement:** All websites managed by the Odoo instance must display a cookie consent banner to comply with the ePrivacy Directive.
* **Functional Logic:** Upon installation, the module must programmatically enable Odoo's native "Cookie Consent Bar" (`cookies_bar` field on the `website` model) for every website record in the database.
* **Prohibition:** The module must not implement its own custom cookie banner. It must strictly leverage the built-in Odoo framework feature.

### B. Safe Legal Page Provisioning
* **Requirement:** The platform must provide standard, editable legal pages for Privacy, Cookies, and Terms of Service.
* **Functional Logic:** The module must create three distinct `website.page` records for the following routes:
    * `/privacy` (Privacy Policy)
    * `/cookie-policy` (Cookie Policy)
    * `/terms` (Terms of Service)
* **Non-Destructive Mandate:** The provisioning process must be non-destructive. If a page already exists at one of these URLs, the module must **not** create a new one or overwrite the existing one. This protects any custom legal text the site administrator may have already put in place.
* **Editability Mandate:** The pages must be created in a way that allows site administrators to edit them using the standard Odoo website builder. Furthermore, these edits must be permanent and protected from being overwritten during subsequent module upgrades.

### C. Documentation Integration
* **Requirement:** A guide explaining the platform's compliance features must be available to administrators within the Odoo backend.
* **Functional Logic:** The module must use a `post_init_hook` to check for the presence of the `knowledge.article` API. If available, it will install a comprehensive guide from a decoupled `data/documentation.html` file.

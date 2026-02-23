# LLM PROJECT SPECIFICATION: MANUAL LIBRARY (`manual_library`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Inheritance:** This specification strictly inherits and enforces all operational mandates, technical standards, and output formatting rules defined in `LLM_GENERAL_REQUIREMENTS.md` and `LLM_ODOO_REQUIREMENTS.md`. 

---

## 1. PROJECT OVERVIEW & STRICT LEGAL MANDATE

**Module Name:** `manual_library`
**Summary:** A clean-room, open-source implementation of a hierarchical documentation and knowledge-base system for Odoo Community. 
**Objective:** To provide a drop-in replacement for the Odoo Enterprise `knowledge` module, allowing other modules (like `user_websites`) to install and manage documentation via standard Odoo XML data loading, without requiring an Enterprise license.

### ⚖️ THE CLEAN-ROOM MANDATE (CRITICAL)
This project is an independent, clean-room implementation. You (the LLM) are strictly bound by the following legal and architectural directives:
1. **No Literal Copying:** You are forbidden from reproducing any source code, XML, JavaScript, or proprietary documentation from the Odoo Enterprise `knowledge` module. 
2. **No Non-Literal Copying:** In accordance with the Abstraction-Filtration-Comparison test (*Computer Associates International, Inc. v. Altai, Inc.*), you must not copy the structural sequence, internal logic flows, or specific non-functional design choices of the original software.
3. **API Interoperability Only:** In accordance with *Google LLC v. Oracle America, Inc.*, you may exactly duplicate the API signatures (Model names, Field names, XML IDs, and Method signatures) required for interoperability. 
4. **Original Implementation:** All underlying business logic, ORM method overrides, security rules, and user interface designs MUST be your own original synthesis of standard Odoo Community framework capabilities.

---

## 2. API SURFACE & DATA MODEL (THE INTERFACE)

To ensure external modules can install documentation using `<record model="knowledge.article" id="...">`, the following API surface must be perfectly exposed. 

**Model:** `knowledge.article`
**Description:** Represents a single page or document within the library.

### Interoperability Fields (Must match exactly):
* `name` (Char): The title of the article. Required.
* `body` (Html): The rich-text content of the article.
* `parent_id` (Many2one to `knowledge.article`): Supports nested, hierarchical documentation.
* `child_ids` (One2many to `knowledge.article`): The inverse of `parent_id`.
* `sequence` (Integer): For manual ordering of sibling articles.
* `is_published` (Boolean): Determines public visibility.
* `icon` (Char): A string representing an emoji or icon class for UI aesthetics.
* `active` (Boolean): Standard Odoo archiving.

### Custom / Original Fields (For our specific implementation):
* `category` (Selection): e.g., 'workspace', 'private', 'shared' (to manage root-level access without copying proprietary permission models).
* `internal_permission` (Selection): 'read', 'write', 'none'.

---

## 3. ORIGINAL FEATURE IMPLEMENTATION SPECIFICATIONS

You must invent the implementation for the following features using standard Odoo Community tools (e.g., standard OWL/JS, QWeb, and the standard `html_editor`).

### A. Hierarchical Navigation (The "Sidebar")
* **Requirement:** Users must be able to navigate the nested structure of articles.
* **Original Implementation Directive:** Do not attempt to reverse-engineer Odoo's complex custom JavaScript workspace sidebar. Instead, implement a standard Odoo Form View combined with a custom QWeb Template or a standard Tree View that visually indents based on the `parent_id` relationship.

### B. Content Editing
* **Requirement:** Users must be able to write rich text.
* **Original Implementation Directive:** Rely entirely on the standard Odoo `html` widget (`<field name="body" widget="html"/>`). Do not implement proprietary real-time collaborative editing algorithms unless achievable purely through standard community mixins.

### C. Web / Public Interface
* **Requirement:** Published articles must be readable on the frontend website.
* **Original Implementation Directive:** Create an original controller (`/manual/<slug>`) that renders a custom QWeb website layout. The layout should feature a navigation menu generated dynamically from `parent_id` relationships.

---

## 4. PERMISSIONS & SECURITY (MAPPING THE "THREE-PERSONA" RULE)

In accordance with the global "Three-Persona" rule defined in `LLM_GENERAL_REQUIREMENTS.md`, the security model for this module maps as follows:

1. **The Owner / Administrator:** * **Mapping:** A dedicated custom security group (e.g., `manual_library.group_manual_manager`).
   * **Rights:** Full CRUD access to all articles.
2. **The Other User (Internal):** * **Mapping:** Standard `base.group_user` (Internal User).
   * **Rights:** Contextual. Can Read articles where `internal_permission` allows. Cannot Write/Create/Delete unless explicitly granted rights on a specific hierarchy branch.
3. **The Guest / Public:** * **Mapping:** Unauthenticated public web users.
   * **Rights:** Contextual. Can Read articles where `is_published = True`. Strictly blocked (403/401) from all mutation attempts.

---

## 5. MODULE-SPECIFIC DEVELOPMENT GUIDELINES

* **Dependency Restriction:** Do not include any standard Odoo Enterprise dependencies in `__manifest__.py`. Depend only on `base`, `web`, `mail`, and `website`.
* **Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER depend on `ham_*` modules or anything else from the proprietary codebase.
* **Global Mandates:** You must strictly follow the AEF output format, Completeness Guarantee, and WCAG accessibility standards as dictated by the global requirements documents.


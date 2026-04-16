# 📚 Manual Library Module (`manual_library`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<architecture>
## 1. Architecture
A clean-room, 100% drop-in API replacement for the proprietary Odoo Enterprise Knowledge module (`knowledge.article`).

## 2. Interoperability
* Dependent modules inject documentation using standard XML records targeting `model="knowledge.article"`.
* **Fields Supported:** `name`, `body` (HTML), `parent_id`, `sequence`, `is_published`, `icon`, `active`, `internal_permission`.
* If the system is upgraded to Enterprise, the table structure allows perfect data retention.
</architecture>

<features>
## 3. Core Features & Logic
* **User Feedback:** Handles user submissions of helpful/not-helpful article ratings via the feedback controller `[@ANCHOR: controller_manual_feedback]`.
* **Search Integration:** Supports live querying of article contents via the search controller `[@ANCHOR: controller_manual_search]`.
* **URL Resolution:** Computes the public website URL path for articles dynamically based on their hierarchy `[@ANCHOR: manual_compute_website_url]`.
* **Structural Integrity:** Strictly enforces parent-child hierarchy checks to prevent recursive or invalid tree structures `[@ANCHOR: manual_check_hierarchy]`.
* **Dynamic TOC:** Automatically parses article HTML on the frontend to generate a dynamic Table of Contents `[@ANCHOR: manual_toc_logic]`.
</features>

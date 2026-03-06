# 📚 Manual Library Module (`manual_library`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Architecture
A clean-room, 100% drop-in API replacement for the proprietary Odoo Enterprise Knowledge module (`knowledge.article`).

## 2. Interoperability
* Dependent modules inject documentation using standard XML records targeting `model="knowledge.article"`.
* **Fields Supported:** `name`, `body` (HTML), `parent_id`, `sequence`, `is_published`, `icon`, `active`, `internal_permission`.
* If the system is upgraded to Enterprise, the table structure allows perfect data retention.

## 3. Semantic Anchors
* `[%ANCHOR: controller_manual_feedback]`, `[%ANCHOR: controller_manual_search]`, `[%ANCHOR: manual_compute_website_url]`, `[%ANCHOR: manual_check_hierarchy]`, `[%ANCHOR: manual_toc_logic]`.

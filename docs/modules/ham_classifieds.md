# 🤝 Ham Radio Classifieds (`ham_classifieds`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Provides a peer-to-peer marketplace. Extends Odoo's `website_sale`. Injects its manual into the Knowledge base upon module installation. [@ANCHOR: doc_inject_ham_classifieds]
</overview>

<security_and_fraud>
## 2. Security & Fraud Prevention
* **`is_ham_classified`** (`Boolean` on `product.template`): Flags a product as a peer-to-peer listing.
* **`classifieds_verification_state`** (`Selection` on `res.users`): Must be `'verified'` to create listings.
* **Strict Creation Override:** The `create()` method explicitly checks verification to block fraud at the ORM layer [@ANCHOR: enforce_classifieds_verification].
* **Proxy Ownership:** Inherits `user_websites.owned.mixin` to restrict edit/delete access strictly to the owner.
</security_and_fraud>

<frontend_interface>
## 3. Frontend Interface
* **Dashboard:** Displays a grid of available listings with dynamic action buttons based on the user's verification state [@ANCHOR: UX_CLASSIFIEDS_UI_GRID].
* **Submission:** Verified users can submit new items directly through a secure frontend HTML form [@ANCHOR: UX_CLASSIFIEDS_HTML_FORM].
</frontend_interface>

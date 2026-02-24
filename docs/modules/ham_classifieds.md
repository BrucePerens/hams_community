# 🤝 Ham Radio Classifieds (`ham_classifieds`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Provides a peer-to-peer marketplace for buying, selling, and trading gear.
It natively extends Odoo's `website_sale` (eCommerce) module but enforces a strict **Secondary Verification Tier** to block callsign-scraping scammers from posting.

---

## 2. Data Model Reference

### Extended `product.template`
* **Inherits:** `user_websites.owned.mixin` (Adds `owner_user_id`).
* **`is_ham_classified`** (`Boolean`): Flags a product as a peer-to-peer classified listing rather than a first-party store product.

### Extended `res.users`
* **`classifieds_verification_state`** (`Selection`): Options include `unverified`, `pending`, `verified`, and `revoked`.

---

## 3. Security & Fraud Prevention
* **Strict Creation Override:** If `is_ham_classified` is set to `True` during record creation, the overridden `create()` method explicitly checks `self.env.user.classifieds_verification_state`. If it is not `'verified'`, the system raises an `AccessError`.
* **Proxy Ownership:** Prevents authenticated users from editing or deleting classified listings that belong to other users.

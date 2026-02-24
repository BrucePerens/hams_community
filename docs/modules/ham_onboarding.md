# 🚀 Ham Radio Onboarding & Identity (`ham_onboarding`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing the source code.

---

## 1. Overview & Core Patterns
Provides foundational callsign management, user onboarding flows, and identity sync hooks. It manages the strict separation between Licensed Operators (`ham`) and Prospective Operators (`swl`), and features a correlation engine to automatically upgrade SWLs when they appear in federal databases.

---

## 2. Data Model Reference

### Extended `res.users`
* **`operator_type`** (`Selection`): `ham` (Licensed Operator) or `swl` (Short Wave Listener / Prospective).
* **`callsign`** (`Char`, Indexed): The user's primary amateur radio callsign. For SWLs, this is forcefully prefixed with `SWL_`.
* **`real_first_name` / `real_last_name` / `zip_code`** (`Char`): Required for SWLs. Used by the correlation engine to match federal license grants.
* **`previous_callsigns`** (`Char`): Comma-separated list of historical callsigns for logbook continuity.
* **`lotw_verified`** (`Boolean`): Indicates cryptographic mTLS verification.
* **`onboarding_method`** (`Selection`): `captcha`, `lotw`, `admin`, `swl_registration`, `other`.

---

## 3. Public Python API & Methods

### On `res.users`:
* **`user.action_update_callsign(new_callsign)`**: Safely updates the user's callsign, updates their `website_slug`, and archives the old callsign.
* **`user.action_upgrade_swl_to_ham(new_callsign)`**: Triggered by the background Callbook sync daemon. Strips the `SWL_` prefix, sets `operator_type` to `ham`, assigns the official callsign, and provisions the associated DNS/Website infrastructure.

---

## 4. Middleware Hooks (mTLS)
The module extends `ir.http._authenticate` to intercept Nginx headers (`X-Client-Verify` and `X-Client-DN`). If a valid LoTW certificate is presented, it auto-logs in the user or redirects a new user to the signup page with a trusted identity token.

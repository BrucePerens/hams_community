# 🚀 Ham Radio Onboarding & Identity (`ham_onboarding`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Manages callsigns, onboarding flows (LoTW mTLS, QRZ, OTP), and identity syncs. Installs operational manuals automatically. [@ANCHOR: doc_inject_ham_onboarding]
</overview>

<identity>
## 2. Callsign & Identity
* **Extended `res.users`**: `callsign`, `previous_callsigns`, `lotw_verified`, `onboarding_method`.
* **`action_update_callsign(new_callsign)`**: Updates the callsign, `website_slug`, and archives the old callsign for logbook continuity, automatically cascading the changes across the database [@ANCHOR: cascade_callsign_update].
</identity>

<verification>
## 3. Verification Pathways
* **mTLS Intercept:** Extends `ir.http._authenticate` to intercept Nginx headers (`X-Client-Verify`). Valid LoTW certificates automatically bypass standard login [@ANCHOR: lotw_mtls_handshake] and consume the generated authentication token [@ANCHOR: lotw_token_consumption].
* **Official OTP:** Generates and dispatches a 6-digit pin to the official email registered with the FCC/ISED [@ANCHOR: UX_GENERATE_OFFICIAL_OTP].
* **QRZ Scraping:** The system polls the user's public QRZ biography looking for a specific validation token [@ANCHOR: UX_VERIFY_QRZ_BIO].
* **Morse Code:** Licensed operators can verify by manually keying their callsign into a web interface [@ANCHOR: UX_PROCESS_MORSE_INPUT], which is then evaluated for accuracy [@ANCHOR: verify_morse_challenge].
</verification>

<anti_spam>
## 4. Anti-Spam
* **Honeypots:** Public signup forms include hidden fields to silently trap and drop automated bot registrations [@ANCHOR: signup_honeypot].
</anti_spam>

<shadow_profiles>
## 5. Shadow Profiles
* Synchronizes user metadata into the operator and SWL index views [@ANCHOR: sync_ham_indices].
</shadow_profiles>

<dependencies>
## 6. External Dependencies
* **Python:** `pika` (Declared in `__manifest__.py`).
</dependencies>
<frontend_tours>
## 7. Frontend Tours
* **Signup Validation:** The frontend registration flows are actively validated via JavaScript UI tours to prevent regressions during framework upgrades [@ANCHOR: test_tour_signup].
</frontend_tours>

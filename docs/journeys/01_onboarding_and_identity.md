# User Journey: Onboarding & Identity Verification

## Phase 1: Registration and Anti-Automation
The user arrives at the account creation portal. If they have their ARRL LoTW `.p12` certificate installed in their browser, accessing the system automatically bypasses the manual sign-up form and securely authenticates them.

If they do not use LoTW, they proceed manually. Instead of selecting images of bicycles, USA-based operators are presented with a randomized technical question from the FCC examination pool (Ham-CAPTCHA). The backend assigns a temporary cryptographic token to the session. A correct answer proves human radio knowledge and allows the account to be generated.

## Phase 2: Proving Ownership
To gain access to protected features like the marketplace, the user must prove they legally hold the callsign. They navigate to the verification dashboard and select a validation path:
1. **Cryptographic Handshake:** *(Reference: `ham_onboarding/controllers/lotw_auth.py` -> `verify_lotw_cert` -> `[ANCHOR: lotw_mtls_handshake]`)* They utilize their ARRL LoTW certificate for instant trust.
2. **Morse Code Transmission:** *(Reference: `ham_onboarding/static/src/js/morse_challenge.js` -> `_decode` -> `[ANCHOR: process_morse_input]`)* An optional challenge where the operator manually taps out their own callsign using the spacebar or UI button. A dynamic clustering algorithm adapts to their specific transmission speed (5 to 40 WPM).
3. **Database Routing:** *(Reference: `ham_onboarding/models/res_users_verification.py` -> `action_send_official_otp` -> `[ANCHOR: generate_official_otp]`)* They request a numeric code dispatched to the official email address cataloged in the federal regulatory directory.
4. **Profile Scraping:** *(Reference: `ham_onboarding/models/res_users_verification.py` -> `action_verify_qrz_bio` -> `[ANCHOR: verify_qrz_bio]`)* They embed a unique system-generated token into their public QRZ.com profile for bot verification.
5. **Manual ID Submission:** If automated methods fail, they securely upload a photo of their official Amateur Radio license, routing a task to the moderation queue for administrator approval.

## Phase 3: Infrastructure Allocation
*(Reference: `ham_dns/models/res_users.py` -> `_provision_personal_dns_zone`)*
The moment the user's identity state changes to verified, the system triggers automated background provisioning. A dedicated subdomain is registered in the nameserver, and the user's account is granted advanced permissions to publish marketplace listings.

# Epics & User Stories: Identity & Onboarding

## Epic: Spam Prevention (Ham-CAPTCHA)
* **Story:** As a prospective USA-based licensed user, I want to answer a technical radio question from the FCC examination pool instead of solving image puzzles during signup, so that I can prove I possess domain knowledge. *(Reference: ham_testing/models/ham_captcha.py -> generate_challenge -> [%ANCHOR: generate_ham_captcha])*
    * **BDD Criteria:** 
        * *Given* an unauthenticated session on the signup page selecting the 'Licensed Operator' path
        * *When* the backend generates a challenge
        * *Then* it MUST return a valid NCVEC question text, 4 choices, and a secure `token`, but MUST NOT expose the correct answer.
* **Story:** As a security architect, I want the challenge system to utilize cryptographically secure, time-limited tokens, so that automated scripts cannot recycle previous answers to bypass the gateway. *(Reference: ham_testing/models/ham_captcha.py -> verify_answer -> [%ANCHOR: verify_ham_captcha])*
    * **BDD Criteria:** 
        * *Given* an active CAPTCHA session older than 15 minutes
        * *When* the user submits the correct answer
        * *Then* the system MUST reject the answer and instantly unlink the expired session record.

## Epic: The SWL (Prospective Ham) Pathway
* **Story:** As someone studying for my license, I want to join the platform without being blocked by technical questions I haven't learned yet, so I can interact with Elmers in the forums.
    * **BDD Criteria:**
        * *Given* an unauthenticated user on the signup page
        * *When* they select the 'SWL' path
        * *Then* the Ham-CAPTCHA is bypassed, standard anti-spam is applied, and their account is created with the `operator_type` set to `swl`.
* **Story:** As a platform defender, I want SWL accounts to be strictly identifiable and sandboxed, so they cannot impersonate licensed operators or flood the DX Cluster.
    * **BDD Criteria:**
        * *Given* an SWL user attempts to modify their profile or submit a log
        * *When* the ORM intercepts the transaction
        * *Then* their login/name MUST be forcefully prefixed with `SWL_`, and the `ham.qso` creation MUST raise an `AccessError`.

## Epic: Automated License Progression
* **Story:** As an SWL who just passed my exam, I want the system to automatically unlock my account the moment the FCC publishes my callsign, without requiring me to email support.
    * **BDD Criteria:**
        * *Given* a background regulatory sync operation
        * *When* an incoming record's exact Name and Zip Code matches an existing SWL account
        * *Then* the system MUST invoke `action_upgrade_swl_to_ham`, transitioning them to a licensed state and provisioning their DNS zone.

## Epic: Procedural Verification & Fallbacks
* **Story:** As a licensed operator proficient in CW, I want an optional challenge to verify my identity by manually transmitting my callsign using the spacebar, adapting to my natural speed between 5 and 40 WPM. *(Reference: ham_onboarding/static/src/js/morse_challenge.js -> _decode -> [%ANCHOR: process_morse_input])*
    * **BDD Criteria:**
        * *Given* a user operating the Morse challenge widget
        * *When* they key their exact callsign at any relative speed
        * *Then* the JS clustering algorithm MUST correctly decode the input and the backend MUST transition their identity state to verified.
* **Story:** As a user unable to use automated verification systems, I want to securely upload a photo of my federal license so an administrator can manually review and approve my account. *(Reference: ham_classifieds/models/res_users.py -> action_request_classifieds_verification)*
    * **BDD Criteria:**
        * *Given* an unverified user uploading an image file
        * *When* the form is submitted
        * *Then* the file MUST be saved as a secure attachment and a `mail.activity` MUST be generated for the `base.user_admin` role.

## Epic: Cryptographic Verification
* **Story:** As an active operator, I want to present my digital `.p12` file to authenticate, so that I can bypass standard login forms and instantly gain trusted status. *(Reference: ham_onboarding/controllers/lotw_auth.py -> consume_lotw_token -> [%ANCHOR: lotw_token_consumption])*
    * **BDD Criteria:** 
        * *Given* a valid `lotw_verified_callsign` payload
        * *When* the account is located or created
        * *Then* `is_identity_verified` and `lotw_verified` MUST be set to True, and the user session automatically established.

## Epic: Identifier Maintenance
* **Story:** As a user who recently changed their assigned callsign, I want the platform to automatically update my login credentials and web addresses based on the regulatory sync, maintaining seamless access. *(Reference: ham_onboarding/models/res_users.py -> action_update_callsign -> [%ANCHOR: cascade_callsign_update])*
    * **BDD Criteria:**
        * *Given* the regulatory daemon detects a callsign change
        * *When* `action_update_callsign` is called via the Service Account
        * *Then* the user's `login`, `callsign`, and `website_slug` MUST be updated simultaneously, and the old callsign MUST be appended to `previous_callsigns`.

# Epics & User Stories: Elmering (Mentorship) Forums

## Epic: High-Trust Educational Environment
* **Story:** As an authenticated user (Ham or SWL), I want to ask technical questions and reply to threads without being repeatedly interrupted by CAPTCHAs, relying on the platform's initial onboarding security to keep the environment spam-free.
    * **BDD Criteria:**
        * *Given* an authenticated user with an active session
        * *When* they submit a new forum post or reply
        * *Then* the system MUST record the post immediately without requiring a Ham-CAPTCHA token validation.

* **Story:** As a reader, I want to instantly know the credentials of the person answering my question, so I can gauge the authority of the advice.
    * **BDD Criteria:**
        * *Given* a rendered forum thread
        * *When* a reply is authored by an explicitly verified operator
        * *Then* the UI MUST render a WCAG-compliant trusted badge pulling their license class directly from `ham.callbook`.

* **Story:** As an Elmer, I want to clearly identify when a question is being asked by a prospective ham who isn't licensed yet, so I can tailor my advice appropriately.
    * **BDD Criteria:**
        * *Given* a rendered forum thread
        * *When* a reply is authored by a user with `operator_type == 'swl'`
        * *Then* the Trust Badge MUST visually distinguish them and display the text "Prospective Ham (SWL)".

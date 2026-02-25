# Proposal 18: SWL Upgrade Acceleration & Fuzzy Matching

## 1. Architectural Context
Short Wave Listeners (SWLs) who pass their exam currently wait up to 24 hours for the nightly regulatory daemon to pull the massive federal database. Furthermore, minor discrepancies in name registration (e.g., "Bob" vs "Robert") cause the exact-match correlation engine to fail, dumping them into a manual moderation queue.

## 2. Integration Design
**Targets:** `ham_onboarding/controllers/settings.py`, `ham_callbook/models/ham_callbook.py`
* **Synchronous "Check Now" API:** Add a button allowing SWLs to request an immediate, targeted fetch against the FCC ULS API for their specific FRN, bypassing the nightly bulk download delay.
* **Fuzzy Name Logic:** Upgrade the correlation engine in `action_request_callsign_upgrade`. If the FRN is missing but the Zip Code matches perfectly, use `difflib.SequenceMatcher` to evaluate the First and Last names. If the similarity ratio is > 85%, accept the match and process the auto-upgrade, bypassing the moderation queue.

## 3. BDD Acceptance Criteria
* **Story:** As a newly licensed operator, I want the system to recognize me even if I used a nickname when signing up.
    * *Given* an SWL registered as "Bob Smith" at "90210"
    * *When* the FCC database lists "Robert Smith" at "90210"
    * *Then* the fuzzy matching engine MUST score the similarity > 85% and automatically upgrade the account to `ham` status.

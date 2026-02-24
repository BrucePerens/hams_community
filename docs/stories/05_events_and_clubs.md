# Epics & User Stories: Events & Clubs

## Epic: Live Net Management
* **Story:** As a Net Control Station (NCS), I want to see a dynamically updating list of participants checking into the frequency, including their specific traffic flags, to maintain orderly communications. *(Reference: ham_events/static/src/js/net_roster_widget.js -> handleCheckin -> [%ANCHOR: live_net_roster])*
    * **BDD Criteria:**
        * *Given* an active net session viewing the OWL UI
        * *When* an `update_checkin` notification is received over the bus
        * *Then* the client-side state array MUST overwrite the existing row without creating duplicate DOM elements.
* **Story:** As a community participant, I want to flag inaccuracies on an event listing, dispatching an automated alert directly to the organizers to ensure the calendar remains reliable. *(Reference: ham_events/controllers/main.py -> report_event_issue -> [%ANCHOR: event_issue_report])*
    * **BDD Criteria:**
        * *Given* a public user submitting the issue form
        * *When* the form contains valid data and an empty honeypot field
        * *Then* the controller MUST escape HTML inputs, log the issue, and use the Service Account to post a note to the event's chatter.

## Epic: Advanced Scoring Algorithms
* **Story:** As an event designer, I want to specify the exact geographic multiplier variables utilized by the backend aggregation routines, ensuring the calculations align with specific rule sets. *(Reference: ham_events/models/ham_contest.py -> action_calculate_scores -> [%ANCHOR: calculate_contest_scores])*
    * **BDD Criteria:**
        * *Given* a contest definition with `scoring_multiplier_type` set to 'grid'
        * *When* the administrator executes `action_calculate_scores`
        * *Then* the dynamic SQL MUST inject `SUBSTRING(gridsquare, 1, 4)` and calculate claimed/confirmed score aggregates directly in Postgres.

## Epic: Organizational Management
* **Story:** As a governance auditor, I want the database layer to inherently reject any ballot submitted by an individual who is not currently active and financially current, mathematically preventing electoral manipulation. *(Reference: ham_club_management/models/survey_extensions.py -> create -> [%ANCHOR: enforce_club_voting_rules])*
    * **BDD Criteria:**
        * *Given* a `survey.user_input` creation request for an `is_club_governance_poll`
        * *When* the submitting user's `membership_state` is expired or they are not a child partner of the club
        * *Then* the ORM MUST abort the transaction and raise a hard `AccessError`.
* **Story:** As a club member, I want a centralized dashboard to view active board elections and my current membership status, so I understand my eligibility to participate in governance. *(Reference: ham_club_management/static/src/xml/club_dashboard.xml -> ClubDashboard -> [%ANCHOR: club_governance_ui])*
    * **BDD Criteria:**
        * *Given* a user accessing their club portal
        * *When* their `membership_state` is anything other than 'paid'
        * *Then* the 'Cast Vote' button on active polls MUST be visually disabled and display a warning regarding their dues.

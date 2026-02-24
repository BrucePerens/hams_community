# User Journey: Club Governance & Voting

## Phase 1: Organizational Setup
A system administrator provisions a new Ham Radio Club by creating a `res.partner` record with the `is_ham_club` boolean checked.
The club is linked to a Collaborative Website Group (`user.websites.group`) to allow its officers to edit the club's public web pages.

## Phase 2: Roster & Dues Management
Using Odoo's native Membership application, the club defines an annual membership fee.
Members purchase or renew their dues via the platform's eCommerce checkout.
Upon payment completion, the member's underlying `res.partner` record is automatically assigned a `membership_state` of `paid`.

## Phase 3: Creating a Governance Poll
A club officer navigates to the Surveys module and creates a new ballot for an upcoming board election.
They check the `is_club_governance_poll` flag and link it to their specific Club.

## Phase 4: Secure Voting
*(Reference: ham_club_management/models/survey_extensions.py -> create -> [%ANCHOR: enforce_club_voting_rules])*
An active member logs into the portal and navigates to `/my/clubs`.
They see their active membership status and click "View Polls" to access the active ballot.
When they submit their vote, the backend ORM intercepts the creation of the `survey.user_input`.
The system executes a hard access check:
1. Does the user's `partner_id.parent_id` match the club?
2. Is the user's `membership_state` currently 'paid' or 'free'?
If both conditions pass, the vote is recorded securely. If not, the system raises an `AccessError`, preventing ballot stuffing.

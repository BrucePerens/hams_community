# 🏛️ Ham Radio Club Management (`ham_club_management`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
A comprehensive suite for local amateur radio clubs.
Tracks membership rosters and dues expiration dates via native Odoo Membership, and facilitates secure, authenticated voting restricted strictly to active, dues-paying members.

---

## 2. Data Model Reference

### Extended `res.partner`
* **`is_ham_club`** (`Boolean`): Flags a partner/company as a Club.
* **`website_group_id`** (`Many2one` to `user.websites.group`): Links the club to its collaborative website.
* **`poll_ids`** (`One2many` to `survey.survey`): Governance polls belonging to the club.

### Extended `survey.survey` (Odoo Surveys)
* **`is_club_governance_poll`** (`Boolean`): Flags the survey as an official club vote.
* **`club_id`** (`Many2one` to `res.partner`): The club owning the poll.

---

## 3. Security & Voting Rules
### Extended `survey.user_input`
The module overrides the `create()` method for survey submissions to enforce strict Club Governance rules.
If `is_club_governance_poll` is True:
1.  **Membership Link Check:** The voting user's `partner_id.parent_id` MUST match the survey's `club_id`.
2.  **Dues Check:** The voting user's `partner_id.membership_state` MUST be either `paid` or `free`.
*Failure to meet these conditions results in a hard `AccessError`, preventing ballot stuffing or non-member voting.*

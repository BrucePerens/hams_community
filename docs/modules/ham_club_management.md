# 🏛️ Ham Radio Club Management (`ham_club_management`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
A comprehensive suite for local amateur radio clubs tracking rosters and dues. The module provides its own technical documentation upon initialization. [@ANCHOR: doc_inject_ham_club_management]
</overview>

<data_model>
## 2. Data Model Reference
* **Extended `res.partner`**: Adds `is_ham_club` (Boolean), `website_group_id`, and `poll_ids`.
* **Extended `survey.survey`**: Adds `is_club_governance_poll` and `club_id`.
</data_model>

<security_and_voting>
## 3. Security & Voting Rules
The module overrides the `create()` method for survey submissions (`survey.user_input`). If `is_club_governance_poll` is True:
1. The voter's `partner_id.parent_id` MUST match the survey's `club_id`.
2. The voter's `membership_state` MUST be `paid` or `free`.
Failure throws an `AccessError` to prevent ballot stuffing.
</security_and_voting>

<governance>
## 4. Governance
* Provides a frontend dashboard for members to manage their status and view polls [@ANCHOR: UX_CLUB_GOVERNANCE_UI].
* Evaluates club voting rules at the ORM layer to ensure the voter is a paid member of the parent club [@ANCHOR: enforce_club_voting_rules].
</governance>

<dependencies>
## 5. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>

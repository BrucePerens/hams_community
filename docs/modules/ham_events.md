# 🏆 Ham Radio Events & Nets (`ham_events`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Tools for organizing on-air events and contests. Provides a real-time Net Control Station (NCS) roster. Installs documentation payloads dynamically on setup. [@ANCHOR: doc_inject_ham_events]
</overview>

<data_model>
## 2. Data Model Reference
* **Extended `event.event`**: `is_ham_net`, `frequency`, `mode`, `net_control_id`.
* **`ham.contest` & `ham.contest.score`**: Tracks `claimed_score` vs `confirmed_score`. The engine dynamically calculates geographic multipliers and aggregates scores [@ANCHOR: calculate_contest_scores].
* **`ham.event.issue`**: Tracks community-submitted event correction reports, notifying organizers of inaccuracies [@ANCHOR: UX_REPORT_EVENT_ISSUE].
</data_model>

<websockets_and_realtime>
## 3. WebSockets & Real-Time Coordination
The `event.registration` model overrides `create()` and `write()` to broadcast live UI updates to Net Control operators, powering the real-time check-in roster [@ANCHOR: UX_LIVE_NET_ROSTER].
</websockets_and_realtime>

<dependencies>
## 4. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>

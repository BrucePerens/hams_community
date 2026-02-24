# 🏆 Ham Radio Events & Nets (`ham_events`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Tools for organizing on-air events, nets, and contests.
It features a real-time Net Control Station (NCS) roster integrated with Odoo's websocket bus, contest scoring definitions, and community-driven event correction reporting.

---

## 2. Data Model Reference

### Extended `event.event`
* **`is_ham_net`** (`Boolean`): Flags the event as an active radio net.
* **`frequency`** (`Float`): The net's operating frequency.
* **`mode`** (`Char`): Operating mode (e.g., SSB).
* **`net_control_id`** (`Many2one` to `res.users`): The assigned Net Control Station.

### Extended `event.registration`
* **`callsign`** (`Char`): The checking-in station.
* **`remarks`** (`Char`): Traffic details.
* **`checkin_status`** (`Selection`): `active` (Active on Net), `traffic` (Has Traffic), `secured` (Checked Out).

### Core Model: `ham.contest`
* **`name`**, **`start_date`**, **`end_date`**, **`exchange_rules`**.
* **`scoring_multiplier_type`** (`Selection`): e.g., DXCC Entities, CQ/ITU Zones.

### Core Model: `ham.event.issue`
* **`event_id`** (`Many2one`): The flagged event.
* **`description`** (`Text`): Issue details.
* **`state`** (`Selection`): `new`, `reviewed`, `resolved`, `dismissed`.

---

## 3. Real-Time Interactions (Websockets)
* **Net Roster Broadcasts:** The `event.registration` model overrides `create()` and `write()` to automatically push real-time check-in updates to the frontend using `self.env['bus.bus']._sendone(f'ham_net_{event_id}', ...)`.

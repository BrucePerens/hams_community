# 📡 Ham Radio Web Shack (`ham_shack`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
The `ham_shack` module serves as the highly interactive OWL-based frontend for active operators. It provides live DX spotting, QSY rig control, Award Tracking (DXCC, WAS, POTA), and On-Air presence broadcasting.

## 2. Data Model Reference

### New Model: `ham.award.progress`
* Tracks user progression toward operating goals (`unworked`, `worked`, `confirmed`).
* **`award_type`**: `DXCC`, `WAS`, `WAC`, `VUCC`, `POTA`.

### Extended `res.users` (Preferences & Presence)
* **`is_on_the_air`**, **`current_frequency`**: Transient presence state.
* **`shack_dark_mode`**, **`shack_audio_alerts`**: UI preferences editable via the "Self-Writeable Fields" idiom without `sudo()`.

## 3. API Surface & WebSockets
* **Lookup API:** `GET /api/v1/ham_shack/lookup/<callsign>` - Queries `ham_callbook` and recent logs for smart auto-fill.
* **Missing Multipliers API:** `GET /api/v1/ham_shack/multipliers` - Returns a dictionary of unworked entities based on `ham.award.progress`.
* **CQ Broadcast:** `user.action_broadcast_cq(frequency, mode)` - Dispatches a bus notification to followers.
* **WebSockets:** Listens to `ham_dx_cluster` to highlight needed spots and trigger HTML5 audio alerts.

## 4. Rig Control & Integrations
* **Local Hardware Relay:** Web browsers issue `fetch` requests to `http://127.0.0.1:8089/qsy` to command local Hamlib (`rigctld`) transceivers.
* **WebSDR Routing for SWLs:** For Prospective Hams (`operator_type == 'swl'`), the QSY action bypasses local hardware and opens an iframe to a public WebSDR node tuned to the target frequency.

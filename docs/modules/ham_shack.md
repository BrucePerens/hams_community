# 📡 Ham Radio Web Shack (`ham_shack`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Highly interactive OWL-based frontend. Provides live DX spotting, QSY rig control, and Award tracking. Injects documentation payloads natively. [@ANCHOR: doc_inject_ham_shack]
</overview>

<models_and_preferences>
## 2. Models & Preferences
* **`ham.award.progress`**: Tracks `award_type` (DXCC, WAS) and `status` (unworked, worked, confirmed).
* **Extended `res.users`**: Tracks transient presence (`is_on_the_air`, `current_frequency`). Users can broadcast their active CQ status to followers [@ANCHOR: broadcast_on_air_presence]. Preference fields like the dark mode toggle [@ANCHOR: web_shack_dark_mode] are explicitly whitelisted as self-writeable.
</models_and_preferences>

<console_features>
## 3. Web Shack Console Features
* **Fast Entry:** Automatically looks up names and locations from the callbook when a callsign is typed [@ANCHOR: UX_FAST_ENTRY_LOOKUP].
* **Live Bandmap:** Highlights incoming DX spots that fulfill missing award multipliers [@ANCHOR: UX_HIGHLIGHT_MISSING_MULTIPLIERS]. Users can configure audio alerts to sound when a needed multiplier is spotted [@ANCHOR: web_shack_audio_alerts].
* **Hardware Integrations:** Operators with physical radios can click QSY to tune their local transceivers via the local proxy at `http://127.0.0.1:8089/qsy` [@ANCHOR: UX_LOCAL_HARDWARE_QSY] [@ANCHOR: local_hardware_qsy]. Unlicensed SWL users clicking QSY are securely routed to an external WebSDR instead [@ANCHOR: swl_websdr_routing].
* **Web Transceiver:** Authorized users can connect to repeaters via WebRTC, offloading all audio traffic directly to the client browser [@ANCHOR: webrtc_direct_client_offload].
</console_features>

<dependencies>
## 4. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>

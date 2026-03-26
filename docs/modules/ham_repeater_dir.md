# 📡 Ham Radio Repeater Directory (`ham_repeater_dir`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Geographical database of local repeaters. Injects its technical manual on installation. [@ANCHOR: doc_inject_ham_repeater_dir]
</overview>

<models_and_security>
## 2. Models & Security
* **`ham.repeater`**: Inherits `user_websites.owned.mixin` to grant Proxy Ownership to individual hams or clubs. [@ANCHOR: repeater_proxy_ownership]
* Tracks `output_frequency`, `is_dmr`, `dcs_code`, etc.
* Supports WebRTC Gateway configuration for VoIP integration.
</models_and_security>

<dependencies>
## 3. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>

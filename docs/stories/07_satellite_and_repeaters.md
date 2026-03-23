# Epics & User Stories: Satellite & Repeaters

## Epic: Satellite Pass Predictions
* **Story:** As a satellite operator, I want to see upcoming pass times (AOS, TCA, LOS) and azimuths for amateur satellites, so I can point my directional antenna. *(Reference: ham_satellite/controllers/main.py -> get_passes -> [@ANCHOR: calculate_satellite_passes])*
    * **BDD Criteria:**
        * *Given* a valid lat/lon or grid square
        * *When* the passes API is invoked
        * *Then* the backend MUST utilize the `ephem` library to return an ordered JSON array of orbital events calculated locally against stored TLEs.
* **Story:** As an operator planning a pass, I want a clean frontend tracking interface to input my grid and see visual predictions.
    * **BDD Criteria:**
        * *Given* a location and time
        * *When* the tracker is queried
        * *Then* the frontend MUST render the calculated satellite passes. *(Reference: [@ANCHOR: UX_FRONTEND_SATELLITE_TRACKER])*

## Epic: Community Repeater Directory
* **Story:** As a club officer, I want to securely manage our club's repeater listings using Proxy Ownership, so that I don't need global administrative rights to update our frequencies. *(Reference: ham_repeater_dir/models/ham_repeater.py -> write -> [@ANCHOR: repeater_proxy_ownership])*
    * **BDD Criteria:**
        * *Given* an authenticated user belonging to a website ownership group
        * *When* they execute a write operation on a `ham.repeater` record mapped to their group
        * *Then* the `_check_proxy_ownership_write` mixin MUST permit the transaction despite lacking backend Admin credentials.

## Epic: Web Transceiver & Remote Operation
* **Story:** As a systems architect, I want all VoIP audio to flow directly between the user's browser and the target repeater, so that the Hams.com server is not subjected to streaming I/O or transcoding computation loads. *(Reference: ham_shack/controllers/api.py -> get_webrtc_credentials -> [@ANCHOR: webrtc_direct_client_offload])*
    * **BDD Criteria:**
        * *Given* an authenticated Web Transceiver session
        * *When* the user transmits audio
        * *Then* the WebRTC connection MUST be established directly with the `webrtc_gateway_uri` and NO audio packets shall be proxied through the Odoo container.

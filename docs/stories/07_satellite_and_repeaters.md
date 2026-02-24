# Epics & User Stories: Satellite & Repeaters

## Epic: Satellite Pass Predictions
* **Story:** As a satellite operator, I want to see upcoming pass times (AOS, TCA, LOS) and azimuths for amateur satellites, so I can point my directional antenna. *(Reference: ham_satellite/controllers/main.py -> get_passes -> [%ANCHOR: calculate_satellite_passes])*
    * **BDD Criteria:**
        * *Given* a valid lat/lon or grid square
        * *When* the passes API is invoked
        * *Then* the backend MUST utilize the `ephem` library to return an ordered JSON array of orbital events calculated locally against stored TLEs.

## Epic: Community Repeater Directory
* **Story:** As a club officer, I want to securely manage our club's repeater listings using Proxy Ownership, so that I don't need global administrative rights to update our frequencies. *(Reference: ham_repeater_dir/models/ham_repeater.py -> write -> [%ANCHOR: repeater_proxy_ownership])*
    * **BDD Criteria:**
        * *Given* an authenticated user belonging to a website ownership group
        * *When* they execute a write operation on a `ham.repeater` record mapped to their group
        * *Then* the `_check_proxy_ownership_write` mixin MUST permit the transaction despite lacking backend Admin credentials.

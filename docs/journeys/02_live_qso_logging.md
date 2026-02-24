# User Journey: Live QSO Logging & Awards

## Phase 1: The Operating Interface
*(Reference: ham_shack/static/src/js/web_shack.js)*
The operator opens the specialized web console. To allow the web browser to send tuning commands to their physical radio hardware without triggering security blocks, they execute a lightweight relay script on their local machine.

## Phase 2: Signal Acquisition
*(Reference: ham_shack/controllers/api.py -> get_missing_multipliers)*
Real-time cluster data flows into the browser interface. The application cross-references the geographic origin of each incoming signal against the operator's internal database of unachieved awards. Signals representing missing regions are visually highlighted. *(Reference: ham_shack/static/src/js/web_shack.js -> checkIfNeeded -> [%ANCHOR: highlight_missing_multipliers])*
The operator clicks the tuning button, routing a frequency shift command through the local relay to the attached transceiver. *(Reference: ham_shack/static/src/js/web_shack.js -> executeQSY -> [%ANCHOR: local_hardware_qsy])*

## Phase 3: Committing the Record
*(Reference: ham_shack/controllers/api.py -> lookup_callsign -> [%ANCHOR: fast_entry_lookup])*
The operator types the target callsign into the input field. The system automatically fetches the target's name and location from the regulatory directory to accelerate data entry.
Upon submission, the backend saves the record. It simultaneously queries the atmospheric tracking table to append the exact solar radiation metrics active at that specific minute. Finally, it alerts the global broadcast service that a new contact has occurred.

## Phase 4: Verification and Interaction
*(Reference: ham_logbook/models/ham_qso.py -> _link_inverse_qsos -> [%ANCHOR: qso_cross_match])*
The application performs a rapid internal scan. If the remote station has also uploaded a matching record within a strict time and frequency tolerance, both records are permanently linked and marked as validated.
If no match is found, the operator can trigger an automated email dispatch, asking the remote station to synchronize their logbook with the platform. *(Reference: ham_logbook/models/ham_qso.py -> action_nudge_station -> [%ANCHOR: qso_nudge_station])*

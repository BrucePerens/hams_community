# Epics & User Stories: DX Cluster & Web Shack

## Epic: The Zero-DB DX Cluster
* **Story:** As an operator, I want to see incoming DX spots appear instantly on my screen via WebSockets, so I can chase rare stations. *(Reference: ham_dx_cluster/static/src/js/dx_cluster_widget.js -> handleSpot -> [%ANCHOR: websocket_pause_toggle])*
    * **BDD Criteria:**
        * *Given* a `new_spot` notification on the `ham_dx_cluster` channel
        * *When* the OWL component processes the payload
        * *Then* the spot MUST be prepended to the array and the array MUST be truncated if length exceeds 50.
* **Story:** As a database administrator, I want the DX Cluster to use an `AbstractModel` and bypass PostgreSQL entirely, pushing spots directly to Redis and the Event Bus, so that high-velocity contest traffic does not cause disk I/O exhaustion. *(Reference: ham_dx_cluster/models/ham_dx_spot.py -> push_spot -> [%ANCHOR: memory_router_push])*
    * **BDD Criteria:**
        * *Given* a spot payload via XML-RPC
        * *When* executed by an authorized daemon/admin
        * *Then* it MUST write to Redis `zadd` and the Odoo `bus.bus` without executing a PostgreSQL `INSERT` on a physical table.
* **Story:** As a visually impaired user, I want a "Pause Updates" button on the live bandmap, so that my screen reader is not overwhelmed by rapid DOM changes. *(Reference: ham_dx_cluster/static/src/xml/dx_cluster_widget.xml -> DXClusterGrid -> [%ANCHOR: a11y_aria_live_toggle])*
    * **BDD Criteria:**
        * *Given* the DX Cluster widget
        * *When* `isPaused` state is toggled to true
        * *Then* `aria-live` MUST change from 'polite' to 'off' and new spots MUST NOT mutate the displayed array.

## Epic: The Ultimate DX Firehose
* **Story:** As a system architect, I want the Firehose daemon to connect directly to PostgreSQL via `asyncpg` and listen for `NOTIFY` events, bypassing the Odoo web workers so we can support tens of thousands of concurrent connections. *(Reference: daemons/dx_firehose/dx_firehose.py -> postgres_notify_handler -> [%ANCHOR: firehose_notify_handler])*
    * **BDD Criteria:**
        * *Given* a PostgreSQL `NOTIFY` on `ham_qso_firehose` containing a comma-separated list of IDs
        * *When* the asyncpg listener intercepts it
        * *Then* it MUST query Postgres using `row_to_json` and broadcast the raw JSON to all authenticated `websockets` clients.

## Epic: The Web Shack Console
* **Story:** As an active operator, I want to type a callsign into the Fast Entry field and have it automatically pull the operator's name and grid square from the regulatory Callbook. *(Reference: ham_shack/controllers/api.py -> lookup_callsign -> [%ANCHOR: fast_entry_lookup])*
    * **BDD Criteria:**
        * *Given* a callsign string in the HTTP GET request
        * *When* the lookup API is hit
        * *Then* it MUST return a JSON payload merging `ham.callbook` directory data with recent `ham.qso` historical context.
* **Story:** As an award chaser, I want the live bandmap to visually highlight incoming spots that fulfill my missing multipliers, so I know exactly who to call. *(Reference: ham_shack/static/src/js/web_shack.js -> checkIfNeeded -> [%ANCHOR: highlight_missing_multipliers])*
    * **BDD Criteria:**
        * *Given* the locally cached `missingMultipliers` object
        * *When* a new spot payload arrives
        * *Then* `isNeeded` MUST evaluate to true if the spot's country/grid matches an unworked multiplier.
* **Story:** As a user with a local physical radio, I want to click a "QSY" button next to a spot, so that a local Python daemon on my PC instructs Hamlib to instantly tune my transceiver. *(Reference: ham_shack/static/src/js/web_shack.js -> executeQSY -> [%ANCHOR: local_hardware_qsy])*
    * **BDD Criteria:**
        * *Given* a frequency and mode
        * *When* `executeQSY` is called
        * *Then* it MUST dispatch a fetch request to `127.0.0.1:8089` avoiding 'undefined' string literals for null modes.

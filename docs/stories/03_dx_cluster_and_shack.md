# Epics & User Stories: DX Cluster & Web Shack

## Epic: The Zero-DB DX Cluster
* **Story:** As an operator, I want to see incoming DX spots appear instantly on my screen via WebSockets, so I can chase rare stations. *(Reference: ham_dx_cluster/static/src/js/dx_cluster_widget.js -> handleSpot -> [@ANCHOR: websocket_pause_toggle])*
    * **BDD Criteria:**
        * *Given* a `new_spot` notification on the `ham_dx_cluster` channel
        * *When* the OWL component processes the payload
        * *Then* the spot MUST be prepended to the array and the array MUST be truncated if length exceeds 50.
* **Story:** As a database administrator, I want the DX Cluster to use an `AbstractModel` and bypass PostgreSQL entirely, pushing spots directly to Redis and the Event Bus, so that high-velocity contest traffic does not cause disk I/O exhaustion. *(Reference: ham_dx_cluster/models/ham_dx_spot.py -> push_spot -> [@ANCHOR: memory_router_push])*
    * **BDD Criteria:**
        * *Given* a spot payload via XML-RPC
        * *When* executed by an authorized daemon/admin
        * *Then* it MUST write to Redis `zadd` and the Odoo `bus.bus` without executing a PostgreSQL `INSERT` on a physical table.
* **Story:** As a database administrator, I want to automatically prune the Redis DX cluster cache every 15 minutes to drop spots older than 4 hours, preventing memory exhaustion. *(Reference: ham_dx_cluster/models/ham_dx_spot.py -> _cron_prune_redis -> [@ANCHOR: cron_prune_dx_redis])*
    * **BDD Criteria:**
        * *Given* the scheduled cron job
        * *When* it executes `_cron_prune_redis`
        * *Then* it MUST use `zremrangebyscore` to purge old spots from Redis.
* **Story:** As a DX node operator, I want my Telnet daemon to push spots securely.
    * **BDD Criteria:**
        * *Given* an external Telnet parser
        * *When* a spot is pushed to the XML-RPC endpoint
        * *Then* it MUST route through the memory router safely. *(Reference: [@ANCHOR: telnet_push_spot])*
* **Story:** As a visually impaired user, I want a "Pause Updates" button on the live bandmap, so that my screen reader is not overwhelmed by rapid DOM changes. *(Reference: ham_dx_cluster/static/src/xml/dx_cluster_widget.xml -> DXClusterGrid -> [@ANCHOR: UX_A11Y_ARIA_LIVE_TOGGLE])*
    * **BDD Criteria:**
        * *Given* the DX Cluster widget
        * *When* `isPaused` state is toggled to true
        * *Then* `aria-live` MUST change from 'polite' to 'off' and new spots MUST NOT mutate the displayed array.

## Epic: The Ultimate DX Firehose
* **Story:** As a system architect, I want the Firehose daemon to connect directly to PostgreSQL via `asyncpg` and listen for `NOTIFY` events, bypassing the Odoo web workers so we can support tens of thousands of concurrent connections. *(Reference: daemons/dx_firehose/dx_firehose.py -> postgres_notify_handler -> [@ANCHOR: firehose_notify_handler])*
    * **BDD Criteria:**
        * *Given* a PostgreSQL `NOTIFY` on `ham_qso_firehose` containing a comma-separated list of IDs
        * *When* the asyncpg listener intercepts it
        * *Then* it MUST query Postgres using `row_to_json` and broadcast the raw JSON to all authenticated `websockets` clients.

## Epic: The Web Shack Console
* **Story:** As an active operator, I want to type a callsign into the Fast Entry field and have it automatically pull the operator's name and grid square from the regulatory Callbook. *(Reference: ham_shack/controllers/api.py -> lookup_callsign -> [@ANCHOR: UX_FAST_ENTRY_LOOKUP])*
    * **BDD Criteria:**
        * *Given* a callsign string in the HTTP GET request
        * *When* the lookup API is hit
        * *Then* it MUST return a JSON payload merging `ham.callbook` directory data with recent `ham.qso` historical context.
* **Story:** As an award chaser, I want the live bandmap to visually highlight incoming spots that fulfill my missing multipliers, so I know exactly who to call. *(Reference: ham_shack/static/src/js/web_shack.js -> checkIfNeeded -> [@ANCHOR: UX_HIGHLIGHT_MISSING_MULTIPLIERS])*
    * **BDD Criteria:**
        * *Given* the locally cached `missingMultipliers` object
        * *When* a new spot payload arrives
        * *Then* `isNeeded` MUST evaluate to true if the spot's country/grid matches an unworked multiplier.
* **Story:** As a user with a local physical radio, I want to click a "QSY" button next to a spot, so that a local Python daemon on my PC instructs Hamlib to instantly tune my transceiver. *(Reference: ham_shack/static/src/js/web_shack.js -> executeQSY -> [@ANCHOR: UX_LOCAL_HARDWARE_QSY])*
    * **BDD Criteria:**
        * *Given* a frequency and mode
        * *When* `executeQSY` is called
        * *Then* it MUST dispatch a fetch request to `127.0.0.1:8089` avoiding 'undefined' string literals for null modes. *(Reference: [@ANCHOR: local_relay_qsy_endpoint])*
* **Story:** As an active operator, I want to click a button to broadcast my CQ presence to followers so they know I'm on the air.
    * **BDD Criteria:**
        * *Given* an authenticated user in the Web Shack
        * *When* they click the 'CQ' broadcast button
        * *Then* the system MUST set their presence to active and dispatch a notification over the bus. *(Reference: [@ANCHOR: broadcast_on_air_presence])*
* **Story:** As a user logging at night, I want a dark mode toggle to reduce eye strain.
    * **BDD Criteria:**
        * *Given* a user toggling the dark mode switch
        * *When* the preference is changed
        * *Then* the UI MUST update and persist the choice via the Self-Writeable Fields idiom. *(Reference: [@ANCHOR: web_shack_dark_mode])*
* **Story:** As a DX hunter, I want audio alerts for needed multipliers.
    * **BDD Criteria:**
        * *Given* a user with audio alerts enabled
        * *When* a needed multiplier arrives on the cluster
        * *Then* the browser MUST synthesize an alert tone using the Web Audio API. *(Reference: [@ANCHOR: web_shack_audio_alerts])*
* **Story:** As an SWL without a transmitter, I want to listen to live DX.
    * **BDD Criteria:**
        * *Given* an SWL user clicking QSY
        * *When* the action executes
        * *Then* the system MUST open a WebSDR iframe tuned to the frequency instead of contacting local hardware. *(Reference: [@ANCHOR: swl_websdr_routing])*

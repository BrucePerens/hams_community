# Epics & User Stories: Logbook & Awards

## Epic: Core Logging & Matching
* **Story:** As an active user, I want to record the specific parameters (frequency, mode, signal strength) of my communications, creating a permanent activity archive. *(Reference: ham_logbook/models/ham_qso.py -> create)*
    * **BDD Criteria:**
        * *Given* a valid QSO dictionary payload
        * *When* submitted to the ORM create method
        * *Then* the record MUST be committed to PostgreSQL and a `NOTIFY` event with the new ID MUST be broadcasted.
* **Story:** As a participant, I want the platform to continuously scan for reciprocal entries from other operators (allowing for slight time and frequency deviations), automatically establishing a verified match without requiring physical cards. *(Reference: ham_logbook/models/ham_qso.py -> _link_inverse_qsos -> [%ANCHOR: qso_cross_match])*
    * **BDD Criteria:**
        * *Given* an unconfirmed QSO record
        * *When* a reciprocal record exists within 15 minutes and 50kHz tolerance
        * *Then* the `inverse_qso_id` on both records MUST be linked, triggering the `platform_confirmed` boolean.
* **Story:** As a user seeking confirmation, I want to trigger an automated dispatch that politely emails the remote station, encouraging them to synchronize their records with the platform. *(Reference: ham_logbook/models/ham_qso.py -> action_nudge_station -> [%ANCHOR: qso_nudge_station])*
    * **BDD Criteria:**
        * *Given* an unconfirmed QSO owned by the requesting user
        * *When* the nudge action is triggered
        * *Then* the system MUST look up the target's email via the Service Account and dispatch the template, OR raise an AccessError if triggered by a non-owner.

## Epic: Third-Party Integration
* **Story:** As a competitive operator, I want to securely store my credentials for external verification networks, allowing a background routine to automatically fetch my latest confirmations. *(Reference: daemons/lotw_eqsl_sync/lotw_eqsl_sync.py)*
    * **BDD Criteria:**
        * *Given* a user with populated `lotw_password` fields
        * *When* the daemon polling cycle initiates
        * *Then* it MUST query the external API using a date-since constraint to prevent full historical downloads.
* **Story:** As a database engineer, I want the background routine to execute cross-matching algorithms entirely within active memory, preventing table locks during large-scale synchronization events. *(Reference: ham_logbook/models/ham_qso.py -> sync_qsl_batch -> [%ANCHOR: qsl_sync_batch])*
    * **BDD Criteria:**
        * *Given* an array of confirmed QSOs from an external provider
        * *When* submitted to `sync_qsl_batch` by the daemon Service Account
        * *Then* it MUST execute a bulk `.write()` on matched records without issuing individual `search()` queries inside the loop.

## Epic: Data Ingestion and Extraction
* **Story:** As a user of desktop software, I want to upload massive data files, triggering an asynchronous worker queue that processes the data without blocking my browser session. *(Reference: ham_logbook/models/ham_adif_queue.py)*
    * **BDD Criteria:**
        * *Given* an ADIF file upload request containing an `X-Idempotency-Key` header
        * *When* received by the API
        * *Then* the system MUST verify the key against Redis to prevent duplicate submissions on network retries, store the file as a Base64 attachment in `ham.adif.queue`, and publish a RabbitMQ task.
* **Story:** As an external developer, I want to query the system for specific paginated data slices, so I can keep third-party applications aligned with the platform. *(Reference: ham_logbook/controllers/api.py -> download_adif)*
    * **BDD Criteria:**
        * *Given* an API GET request with limit and offset
        * *When* the `X-Odoo-Timestamp` is within the 5-minute TTL and the HMAC signature is valid
        * *Then* it MUST return an ADIF-formatted plaintext response limited to the specified window.

## Epic: Environmental Context
* **Story:** As an atmospheric researcher, I want every new entry to automatically pull the exact solar metrics active at that specific minute, providing historical context for long-distance propagation analysis. *(Reference: ham_logbook/models/ham_space_weather.py)*
    * **BDD Criteria:**
        * *Given* a new QSO creation event without supplied weather data
        * *When* the `create` override executes
        * *Then* it MUST fetch the closest preceding `ham.space.weather` record and append SFI, A-Index, and K-Index to the payload.

## Epic: Goal Tracking
* **Story:** As an achievement hunter, I want the system to monitor my progress toward specific geographic operating goals, identifying which regions I have yet to contact. *(Reference: ham_shack/models/award_progress.py)*
    * **BDD Criteria:**
        * *Given* an award definition (e.g., DXCC)
        * *When* queried via the `multipliers` API
        * *Then* it MUST return a JSON structure of unworked entities specific to the requesting user.

# Epics & User Stories: Callbook & Privacy

## Epic: Global Directory Synchronization
* **Story:** As a platform maintainer, I want automated background tasks to routinely ingest massive datasets from international telecommunications authorities, keeping the central repository precise. *(Reference: daemons/fcc_uls_sync/fcc_sync.py -> run_sync -> [%ANCHOR: regulatory_sync_cycle])*
    * **BDD Criteria:**
        * *Given* the daily sync cron job
        * *When* the upstream `ETag` differs from the locally stored `ir.config_parameter`
        * *Then* the daemon MUST download the archive, parse the EN/AM.dat files, and push bulk XML-RPC updates preventing N+1 DB locks.

## Epic: Default Privacy Protection
* **Story:** As a user subject to stringent data protection laws, I want the application to automatically obfuscate my precise street address from public views, ensuring default compliance. *(Reference: ham_callbook/models/ham_callbook.py -> _compute_public_address -> [%ANCHOR: gdpr_address_masking])*
    * **BDD Criteria:**
        * *Given* a `ham.callbook` record
        * *When* the linked user's `privacy_show_in_directory` is False (default)
        * *Then* the computed `public_address` MUST omit the `street` field and append '(Street Withheld)'.

## Epic: Location Obfuscation
* **Story:** As a privacy-conscious individual, I want the mapping engine to mathematically degrade my location precision, centering my marker within a massive geographic boundary rather than pinpointing my exact residence. *(Reference: ham_callbook/models/ham_callbook.py -> _compute_coordinates -> [%ANCHOR: geographic_fuzzing])*
    * **BDD Criteria:**
        * *Given* a 6-character Maidenhead Grid Square (e.g., CM87wu)
        * *When* `grid_privacy_level` is not explicitly set to 'exact'
        * *Then* the compute method MUST truncate the grid to 4 characters (CM87) before executing the lat/lon math conversion.

## Epic: Regulatory Data Retention
* **Story:** As a user exercising my right to be forgotten, I want my personal account destroyed while leaving my historical communication records intact but anonymized, ensuring the platform complies with legal mandates regarding public spectrum usage. *(Reference: ham_logbook/models/res_users.py -> _execute_gdpr_erasure -> [%ANCHOR: anonymize_qso_records])*
    * **BDD Criteria:**
        * *Given* a user executing the GDPR account erasure action
        * *When* the `_execute_gdpr_erasure` override runs
        * *Then* it MUST wipe external passwords, hard-delete pending ADIF queues, and set `owner_user_id` on all their `ham.qso` records to NULL before destroying the user account.

# Epics & User Stories: Infrastructure & Market

## Epic: Trusted Commerce
* **Story:** As a platform defender, I want the database architecture to throw a hard exception if an unverified actor attempts to inject a commercial listing, eradicating fraudulent activity at the lowest possible layer. *(Reference: ham_classifieds/models/product_template.py -> create -> [%ANCHOR: enforce_classifieds_verification])*
    * **BDD Criteria:**
        * *Given* a user whose `classifieds_verification_state` is NOT 'verified'
        * *When* they attempt to create or write to a `product.template` where `is_ham_classified` is True
        * *Then* the ORM MUST raise an `AccessError` halting execution, unless executing via the Proxy Service Account.
* **Story:** As a trusted operator, I want a clean, accessible interface to browse and post equipment listings, with clear visual indicators of my verification status. *(Reference: ham_classifieds/static/src/xml/classifieds_board.xml -> ClassifiedsBoard -> [%ANCHOR: classifieds_ui_grid])*
    * **BDD Criteria:**
        * *Given* a user viewing the classifieds dashboard
        * *When* their `classifieds_verification_state` is 'verified'
        * *Then* the 'Post Item' button MUST be active and accessible, otherwise it MUST be disabled with a prominent verification warning.

## Epic: Advanced Network Routing
* **Story:** As a verified participant, I want the system to automatically generate a dedicated subdomain matching my callsign, providing an immediate anchor for my digital presence. *(Reference: ham_dns/models/res_users.py -> _provision_personal_dns_zone -> [%ANCHOR: provision_personal_dns_zone])*
    * **BDD Criteria:**
        * *Given* a user update transitioning `is_identity_verified` to True
        * *When* intercepted by the `res.users` write method
        * *Then* a `ham.dns.zone` MUST be created via Service Account, mapping `@` and `www` to the configured default A-record IP.
* **Story:** As an individual hosting services on a fluctuating internet connection, I want a standardized HTTP interface that automatically synchronizes my current location with my domain records. *(Reference: ham_dns/controllers/ddns_api.py -> dyndns2_update -> [%ANCHOR: ddns_update_api])*
    * **BDD Criteria:**
        * *Given* a DynDNS2 formatted request (Basic Auth base64 decoded)
        * *When* the password matches a valid `ddns_token` for a dynamic record
        * *Then* the record content MUST be updated to the requesting IP and a `good` response returned.
* **Story:** As an infrastructure architect, I want all DNS modifications to be routed through an asynchronous message broker to an external standalone database, insulating the core application from aggressive query loads. *(Reference: ham_dns/models/ham_dns.py -> trigger_pdns_sync -> [%ANCHOR: trigger_pdns_sync])*
    * **BDD Criteria:**
        * *Given* any CRUD action on `ham.dns.zone` or `ham.dns.record`
        * *When* the transaction completes
        * *Then* a JSON payload containing the action type and IDs MUST be published to the RabbitMQ `dns_zone_updates` queue.

## Epic: Certificate Automation
* **Story:** As a user securing my personal services, I want a specialized integration endpoint that accepts validation strings, allowing my local tools to automatically negotiate and renew cryptographic certificates without manual intervention. *(Reference: ham_dns/controllers/acme_api.py -> acme_update -> [%ANCHOR: acme_challenge_api])*
    * **BDD Criteria:**
        * *Given* a certbot webhook request containing a valid `acme_token`
        * *When* action is 'set'
        * *Then* a TXT record named `_acme-challenge` MUST be created/updated with the provided string wrapped in literal double quotes.

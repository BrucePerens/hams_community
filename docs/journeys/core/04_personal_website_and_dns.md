# User Journey: Personal Websites & DNS Infrastructure

## Phase 1: Automated Delegation
*(Reference: ham_dns/models/res_users.py -> _provision_personal_dns_zone -> [%ANCHOR: provision_personal_dns_zone])*
Upon successful verification of their operating license, the platform triggers an automatic deployment sequence. A background service account generates a new domain zone dedicated to the user. It populates standard routing directives pointing the subdomain to the user's allocated website instance.

## Phase 2: Page Construction
The user visits their assigned web address. Because their account ID is registered as the proxy owner of the layout, the system temporarily elevates their access, exposing the visual site builder. They populate their page with specialized widgets, such as real-time tracking maps or digital displays.

## Phase 3: Infrastructure Expansion
*(Reference: ham_dns/models/ham_dns.py -> trigger_pdns_sync -> [%ANCHOR: trigger_pdns_sync])*
The user decides to host external software on their home network. They access the DNS management console and register a new IPv4 route. The moment the record is saved, the application drops a message onto the internal message bus. The external synchronization worker consumes this message and applies the update to the authoritative nameserver.

## Phase 4: Automation Integration
*(Reference: ham_dns/controllers/ddns_api.py -> dyndns2_update -> [%ANCHOR: ddns_update_api])*
Because their home internet connection uses a shifting address, the user marks the new route as dynamic. The interface provides a unique alphanumeric key. The user programs their home router to transmit this key to the platform's update endpoint, ensuring continuous connectivity.

*(Reference: ham_dns/controllers/acme_api.py -> acme_update -> [%ANCHOR: acme_challenge_api])*
To secure their external software with encryption, the user configures their local certificate tool to transmit cryptographic challenges to the platform's ACME webhook, allowing fully automated certificate renewals.

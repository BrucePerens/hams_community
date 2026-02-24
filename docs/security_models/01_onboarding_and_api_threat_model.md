# Threat Model: Onboarding, Identity & API Boundaries

**Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)

## 1. Spoofing (Impersonating a Valid Operator)
* **Threat:** A malicious actor attempts to claim a high-value callsign to post fraudulent marketplace listings or alter DNS records.
* **Mitigation:** The system utilizes multi-tiered, out-of-band verification. 
    * *High-Trust:* ARRL LoTW verification requires mathematical proof of ownership via a cryptographically signed `.p12` certificate validated by the Nginx edge router against the ARRL Root CA.
    * *Medium-Trust:* Official OTP routes a 6-digit pin exclusively to the email address registered with federal authorities (FCC/ISED), requiring the attacker to compromise the government database or the target's email.

## 2. Tampering (Modifying Data in Transit or at Rest)
* **Threat:** An attacker intercepts an automated ADIF upload and alters the QSO data, or modifies an API request to change a DNS routing.
* **Mitigation:** 
    * In transit: Forced TLS 1.3 across all endpoints.
    * API Security: All headless POST/GET requests require an HMAC-SHA256 signature (`X-Odoo-Signature`) generated using a private `adif_api_secret`. Any tampering with the payload instantly invalidates the hash.

## 3. Repudiation (Denying an Action Occurred)
* **Threat:** A user uploads abusive content or deletes system logs, then denies doing so.
* **Mitigation:** Odoo's native `mail.thread` (chatter) is enabled on all core objects (`ham.qso`, `ham.dns.zone`). Administrative actions taken via Service Accounts actively post immutable chatter logs identifying the invoking user and timestamp.

## 4. Information Disclosure (Exposing Private Data)
* **Threat:** An unauthenticated scraper enumerates the community map to pinpoint exact residential addresses of radio operators.
* **Mitigation:** Geographic Fuzzing is enforced at the ORM compute level. Unless a user explicitly alters their `grid_privacy_level`, the system mathematically truncates their Maidenhead grid to 4 characters, expanding the rendered map pin to a 70x100 mile bounding box.

## 5. Denial of Service (Exhausting System Resources)
* **Threat:** A botnet floods the DX Cluster endpoint with fake spots, or a user uploads a 100MB corrupted ADIF file to lock the web server.
* **Mitigation:** 
    * *DX Cluster:* The `ham.dx.spot` AbstractModel completely bypasses PostgreSQL, routing data to Redis and WebSockets to prevent disk I/O exhaustion.
    * *ADIF:* Uploads are queued instantly as Base64 attachments. Parsing is strictly offloaded to the external `adif_processor` RabbitMQ daemon, shielding the Odoo web workers.
    * *API Idempotency:* Real-time endpoints use an `X-Idempotency-Key` cached in Redis to immediately drop duplicate requests without hitting the database.

## 6. Elevation of Privilege (Gaining Admin Rights)
* **Threat:** An attacker exploits a vulnerability in a custom controller to execute arbitrary code or write to unauthorized tables.
* **Mitigation:** **Zero-Sudo Architecture**. The `.sudo()` method is entirely prohibited. Controllers must impersonate highly restricted Service Accounts (e.g., `user_dns_api_service`) via `with_user()`. If exploited, the attacker inherits only the granular ACLs of that specific proxy account, preventing lateral movement to standard Admin features.

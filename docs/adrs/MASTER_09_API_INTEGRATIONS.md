# MASTER 09: API Integrations & Cryptography

## Status
Accepted (Consolidates ADRs 0011, 0025, 0026, 0028, 0029)

## Context & Philosophy
Communication with third-party networks, local hardware, and headless logging software requires secure, resilient pathways that cannot rely on standard browser cookies.

## Decisions & Mandates

### 1. API Idempotency & HMAC Security (0011)
* External clients logging data via POST MUST provide an `X-Idempotency-Key` validated against a Redis cache to prevent duplicate ingestion upon network retry.
* Payloads must be signed using HMAC-SHA256 with the user's private API secret to bypass CSRF securely.

### 2. Stateless HMAC-TTL Routing Tokens (0025)
* Short-lived access grants (like 1-click unsubscribe links) MUST use stateless, cryptographically signed parameters in the URL including a Unix timestamp, eliminating the need to store and garbage-collect token rows in PostgreSQL.

### 3. Ethical Crawling & Delta Checksums (0026)
* Daemons polling massive external databases (like FCC/BNetzA) MUST respect external servers by evaluating `ETag` and `Last-Modified` headers via `HEAD` requests prior to downloading.
* Downloaded payloads MUST be cryptographically hashed (SHA-256) and verified against the previous state before processing to save CPU cycles.

### 4. At-Rest Encryption for Secrets (0028)
* User credentials for third-party platforms (like LoTW or eQSL) MUST be symmetrically encrypted in PostgreSQL using the system's Fernet `HAMS_CRYPTO_KEY`.

### 5. Hardware-to-Web Airgap Bridge (0029)
* Web browsers block local network requests. Connecting the Web Shack to a physical transceiver requires the `hams_local_relay` daemon. To eliminate onboarding friction, this relay MUST be packaged into native, 1-click OS installers that configure the background service automatically.

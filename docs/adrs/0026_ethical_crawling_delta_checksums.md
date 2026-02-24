# ADR 0026: Ethical Crawling & Delta Checksums

## Status
Accepted

## Context
The platform utilizes numerous background daemons to synchronize global regulatory databases (FCC, ISED, BNetzA) and orbital mechanics data (AMSAT). These files are often massive. If the daemons blindly download and process these files every hour, the platform will consume immense bandwidth, burn CPU cycles parsing unchanged data, and risk being IP-banned by the host agencies.

## Decision
Background daemons interacting with external public APIs MUST perform HTTP header evaluation and payload cryptographic hashing prior to initiating ORM transactions.

1. **Header Check:** The script MUST perform an HTTP `HEAD` or `GET (stream=True)` request to extract `ETag` and `Last-Modified` headers. If these match the stored state in Odoo (`ir.config_parameter`), the daemon must abort immediately.
2. **Hash Check:** If the file is downloaded, the script MUST calculate its SHA-256 hash. If the hash matches the previous run, the file must be discarded and the sync aborted.
3. **Contact Agent:** All requests MUST include a `User-Agent` identifying Hams.com and providing a contact email.

## Consequences
* **Positive:** Respects upstream server resources. Prevents unnecessary database locks and CPU burn. Guarantees operations are truly differential.
* **Negative:** Requires slightly more complex state management, as the daemons must write their resulting hash states back to Odoo upon successful completion.

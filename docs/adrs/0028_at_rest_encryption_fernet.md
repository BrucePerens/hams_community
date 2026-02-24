# ADR 0028: At-Rest Encryption for User Secrets (Fernet)

## Status
Accepted

## Context
Users must provide sensitive third-party credentials (like LoTW or eQSL passwords) to enable background synchronization. Storing these in plaintext within the PostgreSQL database exposes the entire community to credential stuffing attacks if the database is ever compromised.

## Decision
Any third-party user credentials or sensitive integration tokens MUST be symmetrically encrypted at rest using the system's Fernet cryptographic key (`HAMS_CRYPTO_KEY`), and MUST NOT be readable in plaintext via the standard web UI or ORM API by anyone other than the specific syncing Service Account.

1. Model fields storing secrets must use a `_crypt` suffix (e.g., `lotw_password_crypt`).
2. A non-stored, computed field handles the getter/setter logic.
3. The compute method must explicitly verify that the requesting user is the designated Service Account before decrypting and returning the plaintext string. Otherwise, it returns a masked string (e.g., `********`).

## Consequences
* **Positive:** Secures user secrets against database dumps and unauthorized internal access.
* **Negative:** If the master `HAMS_CRYPTO_KEY` is lost or rotated without data migration, all user integrations will break and passwords will be unrecoverable.

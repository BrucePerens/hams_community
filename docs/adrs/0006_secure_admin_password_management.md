# ADR 0006: Secure Admin Password Management & Auto-Hashing

## Status
Accepted

## Context
The Odoo application requires a master administrator password (`base.user_admin`) to manage the system via the UI. Historically, this was stored in plaintext within `odoo.conf`, XML initialization files, or the `.env` vault. Storing plaintext passwords in any configuration file or vault is a critical vulnerability. However, if an administrator places a pre-hashed password directly into the `.env` file, Odoo's ORM intercepts the write operation and hashes the string a second time (the "double-hash" problem), rendering the account inaccessible.

## Decision
We will strictly prohibit the storage of plaintext admin passwords across the entire repository and infrastructure vaults. To solve the double-hash problem, we are implementing a split-layer ingestion architecture:

1. **The CLI Utility:** Administrators MUST use the interactive `tools/hash_admin_password.py` script. This script prompts for a password, generates an Odoo-compliant `pbkdf2_sha512` hash, and automatically mutates the `deploy/.env` file to inject the secure hash.
2. **The SQL Bypass Hook:** During deployment or module upgrades, the `ham_init` module's `post_init_hook` reads the `ODOO_ADMIN_PASSWORD` from the environment. If it detects the `$pbkdf2-sha512$` cryptographic signature, it explicitly bypasses the ORM's `write()` method and uses a parameterized raw SQL `UPDATE` statement. This injects the hash directly into PostgreSQL, circumventing the double-hash trap.

## Consequences
* **Positive:** The `.env` file is scrubbed of UI plaintext passwords. If the vault is read by an unauthorized actor, the admin password remains cryptographically secure.
* **Negative:** Administrators can no longer manually type a plaintext password into the `.env` file. They must rely on the provided Python utility to rotate credentials.

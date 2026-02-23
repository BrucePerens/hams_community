# ADR 0006: Secure Admin Password Management & Auto-Hashing

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
The Odoo application requires a master administrator password to manage the system via the UI. Historically, this was stored in plaintext within `odoo.conf` or `.env` files. Storing plaintext passwords in any configuration file or vault is a vulnerability. However, if an administrator places a pre-hashed password directly into the `.env` file, Odoo's ORM intercepts the write operation and hashes the string a second time (the "double-hash" problem), rendering the account inaccessible.

## Decision
We will strictly prohibit the storage of plaintext admin passwords across the entire repository and infrastructure vaults. To solve the double-hash problem, we implement a split-layer ingestion architecture:
1. **The CLI Utility:** Administrators MUST use the interactive `tools/hash_admin_password.py` script to automatically mutate `.env` files with secure `pbkdf2_sha512` hashes.
2. **The SQL Bypass Hook:** During deployment, initialization modules must bypass the ORM's `write()` method and use a parameterized raw SQL `UPDATE` statement to inject the hash directly into PostgreSQL, circumventing the double-hash trap.

## Consequences
* **Positive:** The `.env` file is scrubbed of UI plaintext passwords.
* **Negative:** Administrators can no longer manually type a plaintext password into the `.env` file.

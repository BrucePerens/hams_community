# ADR 0031: PostgreSQL Trigram Indexing for Callsigns

## Status
Accepted

## Context
Searching for callsigns often requires partial matching (e.g., searching `W1A%` to find `W1AW`). Standard PostgreSQL B-Tree indexes cannot optimize `ILIKE` or partial string searches, resulting in sequential table scans. In tables like `ham.qso` and `ham.callbook`, this creates massive performance degradation as the row count enters the millions.

## Decision
Any core model containing an Amateur Radio Callsign that expects to be queried via partial strings or `ILIKE` operations MUST implement `index='trigram'` on the field definition.

This forces Odoo to leverage PostgreSQL's `pg_trgm` extension, which breaks strings into 3-letter chunks to build an index highly optimized for fuzzy searching and `ILIKE` queries.

## Consequences
* **Positive:** Sub-millisecond response times for partial callsign lookups (like the Web Shack auto-fill API) even on massive tables.
* **Negative:** Trigram indexes take up more disk space and slightly increase the overhead of `INSERT` and `UPDATE` operations compared to standard B-Trees.

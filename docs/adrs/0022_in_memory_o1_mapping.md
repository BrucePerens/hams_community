# ADR 0022: Bounded Chunking, Iteration & Memory Mapping

## Status
Accepted

## Context
Processing massive datasets (like external Callbook syncs, GDPR erasures, or massive QSL logs) frequently leads to N+1 database locks or Out-Of-Memory (OOM) WSGI crashes.
However, simply placing a `limit` on a mass operation (like data deletion) without implementing an iterative loop causes the system to process the first chunk and silently ignore the rest, causing severe regulatory and functional failures. Furthermore, dumping massive arrays into `json.dumps()` for data exports causes immediate memory exhaustion.

## Decision
Any method processing, mutating, or exporting unbounded arrays of data MUST utilize Bounded Iteration and Memory Mapping:

1. **Mutative Iteration (`while True` loops):** Operations that delete or modify unbounded amounts of data (e.g., GDPR Erasure, Content Unpublishing) MUST use a `while True` loop with a fixed `limit` (e.g., 5000). The loop must process the batch, update the database, and repeat until the search yields no results.
2. **Streaming Generators for Exports:** Endpoints generating massive JSON payloads (like GDPR Data Portability exports) MUST NOT use `json.dumps()` on monolithic dictionaries. They MUST implement Python generators (`yield`) that output string-formatted JSON chunks iteratively, allowing the server to stream the HTTP response with a completely flat O(1) memory footprint.
3. **Pre-Fetch & O(1) Mapping:** When synchronizing two datasets (e.g., incoming ADIF logs vs. existing database records), extract the unique IDs/keys first. Pre-fetch the matching Odoo records in a single bounded query. Construct a Python dictionary mapped to those keys for O(1) lookups, preventing `.search()` calls inside the `for` loop.
4. **Batch Commit:** Commit updates using bulk `.write()` or `create()` operations at the end of each chunk's lifecycle, rather than one record at a time.

## Consequences
* **Positive:** Eliminates N+1 database locks. Guarantees 100% data processing compliance for regulations without risking OOM crashes. Allows users with millions of log entries to instantly download their data.
* **Negative:** Requires more complex iteration logic and forces developers to write custom JSON string-building generators instead of relying on native library serialization.

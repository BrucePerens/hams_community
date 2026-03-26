# 📻 Ham Logbook (`ham_logbook`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Provides the `ham.qso` model. Enforces GDPR exemptions for public RF records. It injects its technical manual on install. [@ANCHOR: doc_inject_ham_logbook]
</overview>

<models>
## 2. Models
* **`ham.qso`**: Contact log. The system automatically attempts to cross-index new entries against reciprocal logs [@ANCHOR: qso_cross_match]. If unconfirmed, users can trigger an email to nudge the remote station [@ANCHOR: UX_QSO_NUDGE_STATION]. During GDPR deletion, `owner_user_id` uses `ondelete='set null'` to anonymize rather than delete [@ANCHOR: anonymize_qso_records].
* **`ham.adif.queue`**: Async staging for file uploads. Users can upload via the web UI [@ANCHOR: UX_HUMAN_ADIF_UPLOADER] which triggers a web task [@ANCHOR: web_enqueue_adif_task], or via API [@ANCHOR: api_enqueue_adif_task].
* **`ham.space.weather`**: Stores NOAA SFI/K-Index telemetry.
</models>

<apis_and_sync>
## 3. APIs & Synchronization
* **ADIF Upload/Download**: Protected by HMAC-SHA256 timestamp/payload signatures via `adif_api_secret`.
* **Live Logging**: Rejects duplicate submissions via Redis [@ANCHOR: api_idempotency_check]. Immediately triggers the DX Firehose Postgres `NOTIFY` [@ANCHOR: qso_firehose_notify].
* **External QSLs**: The module processes bulk confirmation arrays from external networks natively in RAM [@ANCHOR: qsl_sync_batch].
</apis_and_sync>

<dependencies>
## 4. External Dependencies
* **Python:** `pika`, `cryptography` (Declared in `__manifest__.py`).
</dependencies>

# Proposal 17: Human-Centric ADIF Drag-and-Drop Uploader

## 1. Architectural Context
The platform possesses a highly secure, idempotent REST API for ADIF uploads designed for headless desktop software (e.g., WSJT-X). However, it lacks a graphical interface for human operators to manually upload their exported `.adi` files using standard web sessions.

## 2. Integration Design
**Targets:** `ham_logbook/controllers/website_logbook.py`, `ham_logbook/views/logbook_templates.xml`
* **Session-Based Endpoint:** Create a new controller route (`POST /my/logbook/web_upload`) that relies on native Odoo session cookies and standard CSRF tokens instead of requiring the user to generate an HMAC `adif_api_secret`.
* **OWL Drag-and-Drop Component:** Create a modern frontend dropzone on the `/my/logbook` page. When a file is dropped, it posts to the new endpoint, which securely creates the `ham.adif.queue` record.
* **Live Progress Bar:** The OWL component polls the queue record's `state` and `records_processed` fields to render a live progress bar, terminating in a success toast notification when the background daemon finishes.

## 3. BDD Acceptance Criteria
* **Story:** As a human operator, I want to drag my ADIF file into the browser and watch it process.
    * *Given* an authenticated session on the Logbook UI
    * *When* an ADIF file is dropped into the dropzone
    * *Then* it MUST upload via the CSRF-protected session route, spawn a queue record, and visually update the progress bar.

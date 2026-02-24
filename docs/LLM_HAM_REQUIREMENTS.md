# AMATEUR RADIO OPERATIONAL MANDATES & EXEMPTIONS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

**Inheritance:** This document extends `LLM_GENERAL_REQUIREMENTS.md`. The rules defined here supersede global mandates where explicit exemptions are granted for Amateur Radio operations.

---

## 1. 📡 Data Privacy (GDPR) & Public Records

### A. The GDPR Erasure Exemption (QSO Logs)
Amateur radio transmissions (QSOs) are, by definition and international law, broadcast in the clear using public RF spectrum. They are intended for public reception and constitute a matter of public record.

* **The Exemption:** Because of this public broadcast nature, QSO logging data (`ham.qso`) is **strictly exempt** from the GDPR/CCPA "Right to Erasure" mandates defined in `LLM_GENERAL_REQUIREMENTS.md`.
* **Technical Mandate:** 
    * You MUST NEVER architect a system that cascades deletion to a `ham.qso` record. 
    * Any relational field linking a `ham.qso` to a `res.users` or `res.partner` MUST use `ondelete='set null'` or `ondelete='restrict'`. Never `cascade`.
    * When extending the `_execute_gdpr_erasure()` hook for the logbook module, you must explicitly bypass QSO records, leaving them as anonymized historical records.

### B. QTH (Location) Data Masking
While FCC data (including home addresses) is public record in the USA, European operators fall under GDPR. 

* **The Mandate:** The `ham_callbook` module MUST implement a strict data-masking layer. By default, it may only display non-PII data (Callsign, Grid Square, CQ/ITU Zones) for unauthenticated or public views. Displaying precise addresses or unlisted emails MUST be governed by an explicit opt-in boolean on the user's profile.

---

## 2. 🌐 User Websites & Routing Architecture

* **Separation of Concerns:** The `user_websites` module MUST remain a generic provider. It routes and provisions sites based on a generic `website_slug` field on the `res.users` model.
* **Callsign Injection:** Domain-specific modules (like `ham_onboarding`) are strictly responsible for injecting and maintaining that `website_slug` with the user's callsign. 
* **Callsign Changes:** When a callsign changes (e.g., via FCC sync), `ham_onboarding` must update the `website_slug`. The `user_websites` module will automatically detect this change and provision the necessary 301 redirects.

---

## 3. ♿ Accessibility (WCAG) for Real-Time Grids

Amateur radio tools heavily utilize real-time data feeds (e.g., DX Cluster Bandmaps, Net Control Rosters).

* **The Mandate:** Rapidly updating DOM elements are actively hostile to screen readers. Wrapping a highly volatile grid in standard `aria-live="polite"` is FORBIDDEN as it will cause constant interruptions.
* **Implementation:** Real-time OWL components MUST implement a "Pause Updates" or "Screen Reader Mode" toggle. Background DOM updates must be hidden from the accessibility tree (`aria-live="off"`) unless the user explicitly requests an update, or updates must be batched and summarized.

---

## 4. 🚀 Performance & ORM Exhaustion (Ephemeral Data)

Major contests generate thousands of DX spots per hour.

* **The Mandate:** Modules handling volatile, high-velocity data (like `ham_dx_cluster`) MUST NOT rely on permanent PostgreSQL ORM storage without an aggressive lifecycle policy.
* **Implementation:** DX spots must either bypass the DB (brokered through an external Redis cache to the OWL frontend) OR the module must include an automated Cron job that hard-deletes `ham.dx.spot` records older than 4 hours to prevent database bloat and WSGI worker exhaustion.

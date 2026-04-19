# Global Fallback Strategy for Callbook Verification

## Problem Statement
While some countries (e.g., Canada, Japan) provide unrestricted public open data for amateur radio operators, many countries strictly enforce privacy laws (GDPR, APPs, POPIA) and prohibit the mass publication of personally identifiable information (PII). In these jurisdictions (e.g., Australia, Netherlands, Ireland, South Korea, etc.), bulk databases are explicitly blocked or heavily redacted.

Since our daemon has an ethical and regulatory obligation to verify that an operator holds a valid license before granting access to remote transmitters, we cannot rely solely on bulk national downloads.

## The Verification Strategy

The implementation daemon should employ a **Three-Tiered Verification Strategy** for international callsigns.

### Tier 1: National Bulk Databases (When Available)
If the user's callsign belongs to a country documented in our repository that provides bulk data (e.g., USA, Canada, Japan), the daemon should query our locally synced copy of that national database.
- *Pros:* High accuracy, offline capability, definitive legal source.
- *Cons:* Only covers a subset of global nations.

### Tier 2: Real-time International Aggregators (The Fallback)
If the callsign belongs to a country without a public bulk database (or if Tier 1 fails), the daemon should query an established international aggregator API.

**Recommended Aggregator APIs:**
1. **HamQTH XML API (Free)**
   - Highly recommended for automated daemons.
   - Endpoint: `https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`
   - Data structure includes name, class, and location.
2. **QRZ.com XML API (Requires Subscription)**
   - The largest global database, but automated API access requires an XML Logbook subscription.
   - Endpoint: `https://xmldata.qrz.com/xml/current/?s={session_id}&callsign={callsign}`

- *Pros:* Excellent global coverage; many privacy-restricted operators voluntarily list themselves here to facilitate QSL card exchanges.
- *Cons:* Relies on third-party uptime; some operators choose not to list themselves even on QRZ.

### Tier 3: Manual Verification Pipeline
If an operator is entirely missing from both National databases and International aggregators (which is common for new licensees in privacy-restricted nations), the automated daemon must fail gracefully and enter a manual verification state.

1. Prompt the user: `"Your callsign could not be automatically verified in public databases. Please upload a clear photo or PDF of your official Amateur Radio License Certificate."`
2. The user uploads their certificate (e.g., Ofcom PDF, ACMA email, RDI screenshot).
3. The system routes the document to a human administrator (or a specialized OCR/LLM vision model) to verify the license validity and class before granting transmitter access.

# New Zealand Amateur Radio Operator Database

## Source Information
- **Agency:** Radio Spectrum Management (RSM) - Ministry of Business, Innovation & Employment
- **Database Name:** Register of Radio Frequencies (RRF)
- **Source URL:** https://www.rsm.govt.nz/licensing/how-do-i/use-the-rrf/search-the-rrf/search-callsigns
- **License/Redistribution:** NZ Government Open Data / Crown Copyright.

## Download / Verification Process
The RSM maintains the Register of Radio Frequencies (RRF). While the online database allows searching for all callsigns (by leaving the search field blank), the ability to export the complete list as a CSV is restricted to "Authorised users" who are logged in via RealMe.

### Scraping / Verification Strategy
Since automated access to a bulk CSV is restricted behind authentication for New Zealand residents:
1. **Interactive Query:** The daemon should perform an HTTP POST or GET to the public RRF search page to verify individual callsigns as needed.
2. **Community Aggregators (Fallback):** The New Zealand Association of Radio Transmitters (NZART) occasionally publishes callbook lists for its members, or international aggregators like QRZ/HamQTH can be used as a fallback if the RRF public search is rate-limited.

**Example RRF Search Endpoint:**
The exact endpoint requires analyzing the RRF web form at `https://rrf.rsm.govt.nz/` (or similar subdomains like `smart.rsm.govt.nz`).

## Data Format & Schema
When querying the RRF public interface for a specific callsign, the expected fields are:
- `Callsign`: (e.g., ZL...)
- `Client Name`: The name of the license holder or club.
- `Location`: Varies, but usually contains general geographic information.

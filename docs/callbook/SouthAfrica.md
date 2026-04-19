# South Africa Amateur Radio Operator Database

## Source Information
- **Agency:** Independent Communications Authority of South Africa (ICASA) / South African Radio League (SARL)
- **Primary Source:** SARL Callbook (Online interactive search)
- **Aggregator / Community Source:** `https://mysarl.org.za/`
- **License/Redistribution:** South African amateur radio data is not available as a bulk government open-data CSV. It is primarily managed via ICASA but the definitive public searchable database is maintained by SARL (the national amateur radio society).

## Download / Verification Process
There is no bulk download CSV provided by ICASA or SARL for current active operators. (SARL does provide a PDF archive for historical data from 1926-1997, but this is not useful for verifying current active transmitters).

To verify a license, the daemon must scrape or query the SARL online callbook form.
The exact form URL may shift, but it is typically located within the SARL member portal or main website.

### Scraping Strategy (Interactive Query)
Because there is no bulk data, the daemon will need to dynamically construct requests to the SARL callbook form (or rely on international aggregators like HamQTH / QRZ if SARL proves too difficult to scrape reliably).

**Querying an International Aggregator (Fallback):**
If the local SARL database blocks automated queries, checking South African calls (ZS, ZR, ZU prefixes) against international APIs is the recommended fallback:
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

## Data Format & Schema
When scraping a specific callsign, the expected fields are:
- `Callsign`: (e.g., ZS6...)
- `Name`
- `License Class`: (e.g., Class A / Full, Class B / Restricted)
- `Status`: Valid/Active

*Note: Like Australia, be aware that many operators may opt-out of having their exact address published online in the SARL directory.*

# Mexico Amateur Radio Operator Database

## Source Information
- **Agency:** Instituto Federal de Telecomunicaciones (IFT)
- **Database Name:** Registro Público de Concesiones (RPC)
- **License/Redistribution:** Mexican telecommunications law requires commercial concessions to be public, but individual amateur radio (Radioaficionados) licenses are often treated as private personal data. 

## Important Notice on Privacy
The IFT does not provide a straightforward, bulk downloadable CSV of all individual amateur radio operators on their open data portal.

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source or targeted scraping must be used.

## Source Information (Secondary Aggregator)
- **Aggregator Example:** Federación Mexicana de Radioexperimentadores (FMRE)
- **International Fallbacks:** HamQTH, QRZ.com (XE, XF prefixes).

## Download / Verification Process
There is no bulk download CSV easily accessible for Mexican operators.

To verify a Mexican license, the daemon should query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If the operator is unlisted, require a manual upload of their IFT `Concesión de Uso Privado con propósitos de Radioaficionado`.

### Data Schema (Expected fields from queries)
When querying a Mexican callsign via an aggregator, expect to find:
- **Callsign:** e.g., XE1...
- **Name:** (If voluntarily provided)
- **Location:** State/City.

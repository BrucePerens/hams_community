# Spain Amateur Radio Operator Database

## Source Information
- **Agency:** Secretaría de Estado de Telecomunicaciones e Infraestructuras Digitales (Telecommunications Secretariat) / Unión de Radioaficionados Españoles (URE)
- **Database Name:** URE Callbook / Telecomunicaciones Public Register
- **License/Redistribution:** The Spanish government strictly protects the privacy of amateur radio operators in compliance with the GDPR (LOPD in Spain).

## Important Notice on Privacy
In Spain, there is **no public bulk database** of amateur radio operators provided by the telecommunications authority. The general public cannot download a list of callsigns or addresses. 

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source must be used.

## Source Information (Secondary Aggregator)
- **Aggregator Example:** The Unión de Radioaficionados Españoles (URE) maintains a callbook, but access to detailed information often requires membership and logging in. 
- **International Fallbacks:** HamQTH, QRZ.com (EA, EB, EC prefixes).

## Download / Verification Process
There is no bulk download CSV provided by the Spanish government.

To verify a Spanish license, the daemon must query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If a Spanish operator is not listed in international databases, verification may require the operator to upload a digital copy or photograph of their official license manually.

### Data Schema (Expected fields from queries)
When querying a Spanish callsign via an aggregator, expect to find:
- **Callsign:** e.g., EA...
- **Name:** (If voluntarily provided)
- **Location:** Province or city.

# Netherlands Amateur Radio Operator Database

## Source Information
- **Agency:** Rijksinspectie Digitale Infrastructuur (RDI) - formerly Agentschap Telecom (AT)
- **Database Name:** Frequentieregister (User Portal / Mijn RDI)
- **License/Redistribution:** The Dutch telecommunications regulator (RDI) strictly protects the privacy of amateur radio operators. The registry is closed and not available as open data.

## Important Notice on RDI Privacy
In the Netherlands, there is **no public bulk database** of amateur radio operators provided by the RDI. The general public cannot download a list of callsigns or addresses.
The RDI requires individuals to log into the "Mijn RDI" portal using DigiD (a secure government digital identity) to manage their own callsigns. They do not publish a searchable directory for third parties due to strict adherence to the GDPR (AVG - Algemene Verordening Gegevensbescherming).

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source must be used.

## Source Information (Secondary Aggregator)
Since RDI does not provide public data, developers must rely on community-maintained databases or international aggregators.
- **Aggregator Example:** VERON (Vereniging voor Experimenteel Radio Onderzoek in Nederland) sometimes maintains internal lists for members, but these are not bulk accessible.
- **International Fallbacks:** HamQTH, QRZ.com, or European aggregators.

## Download / Verification Process
There is no bulk download CSV provided by RDI.

To verify a Dutch license (Prefixes: PA, PB, PC, PD, PE, PF, PG, PH, PI), the daemon must query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If a Dutch operator is not listed in international databases, verification may require the operator to upload a digital copy or photograph of their RDI registration certificate manually.

### Data Schema (Expected fields from queries)
When querying a Dutch callsign via an aggregator, expect to find:
- **Callsign:** e.g., PA0... or PD0...
- **Name:** (If voluntarily provided to the aggregator)
- **License Class:** Full (F) or Novice (N). (This is usually inferable from the prefix, e.g., PD is Novice, PA/PE/PB are Full).

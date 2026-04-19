# South Korea Amateur Radio Operator Database

## Source Information
- **Agency:** Korea Communications Agency (KCA) / Korean Amateur Radio League (KARL)
- **License/Redistribution:** The South Korean telecommunications regulator (KCA) does not provide a public bulk data export of amateur radio operator data due to South Korean personal information protection laws.

## Important Notice on KCA Privacy
In South Korea, there is **no public bulk database** of amateur radio operators provided by the KCA.
The general public cannot download a list of callsigns or addresses. 

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source or interactive verification must be used.

## Source Information (Secondary Aggregator)
Since KCA does not provide public open data, verification requires relying on the Korean Amateur Radio League (KARL) member lookup or international aggregators.
- **Aggregator Example:** KARL (Korean Amateur Radio League) maintains member callsign directories, but they are not provided as bulk open data.
- **International Fallbacks:** HamQTH, QRZ.com (HL, DS, 6K prefixes).

## Download / Verification Process
There is no bulk download CSV provided by KCA.

To verify a South Korean license (Prefixes: HL, DS, 6K, D7, D8, D9), the daemon must query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If a South Korean operator is not listed in international databases, verification may require the operator to upload a digital copy or photograph of their KCA registration certificate manually.

### Data Schema (Expected fields from queries)
When querying a South Korean callsign via an aggregator, expect to find:
- **Callsign:** e.g., HL... or DS...
- **Name:** (If voluntarily provided)
- **Location:** City or province (e.g., Seoul, Gyeonggi).

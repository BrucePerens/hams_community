# Italy Amateur Radio Operator Database

## Source Information
- **Agency:** Ministero delle Imprese e del Made in Italy (MIMIT) - formerly MISE
- **Database Name:** MIMIT Telecomunicazioni Registries / Associazione Radioamatori Italiani (ARI)
- **License/Redistribution:** Italian amateur radio data is not available as a public bulk government open-data CSV due to EU GDPR privacy regulations.

## Important Notice on Privacy
In Italy, there is **no public bulk database** of amateur radio operators provided by MIMIT. 

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source must be used.

## Source Information (Secondary Aggregator)
- **Aggregator Example:** Associazione Radioamatori Italiani (ARI) maintains callbooks and QSL bureau listings, but they do not provide bulk CSV downloads.
- **International Fallbacks:** HamQTH, QRZ.com (I, IK, IN, IT, IW, IZ prefixes).

## Download / Verification Process
There is no bulk download CSV provided by the Italian government.

To verify an Italian license, the daemon must query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If an Italian operator is not listed in international databases, verification may require the operator to upload a digital copy or photograph of their official MIMIT `Autorizzazione Generale` manually.

### Data Schema (Expected fields from queries)
When querying an Italian callsign via an aggregator, expect to find:
- **Callsign:** e.g., IZ...
- **Name:** (If voluntarily provided)
- **Location:** City or region.

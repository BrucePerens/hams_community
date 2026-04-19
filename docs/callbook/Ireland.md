# Ireland Amateur Radio Operator Database

## Source Information
- **Agency:** Commission for Communications Regulation (ComReg) / Irish Radio Transmitters Society (IRTS)
- **Database Name:** eLicensing Portal / Amateur Station Licence 
- **Source URL:** https://www.comreg.ie/industry/radio-spectrum/licensing/search-licence-type/radio-amateurs-2/
- **License/Redistribution:** The Irish telecommunications regulator (ComReg) strictly protects the privacy of amateur radio operators. The registry is closed and not available as a bulk open data CSV.

## Important Notice on ComReg Privacy
In Ireland, there is **no public bulk database** of amateur radio operators provided by ComReg. The general public cannot download a list of callsigns or addresses. 
ComReg requires individuals to log into their eLicensing portal to manage their own callsigns and does not publish a searchable directory for third parties, adhering to GDPR.

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source must be used.

## Source Information (Secondary Aggregator)
Since ComReg does not provide public data, developers must rely on community-maintained databases or international aggregators.
- **Aggregator Example:** The Irish Radio Transmitters Society (IRTS) provides some callbook features, but it is typically restricted or incomplete.
- **International Fallbacks:** HamQTH, QRZ.com, or QRZCQ.

## Download / Verification Process
There is no bulk download CSV provided by ComReg.

To verify an Irish license (Prefixes: EI, EJ), the daemon must query an international aggregator.
`GET https://api.hamqth.com/call?callsign={callsign}&prg={session_id}`

If an Irish operator is not listed in international databases, verification may require the operator to upload a digital copy or photograph of their ComReg registration certificate manually.

### Data Schema (Expected fields from queries)
When querying an Irish callsign via an aggregator, expect to find:
- **Callsign:** e.g., EI...
- **Name:** (If voluntarily provided to the aggregator)
- **License Class:** Full (Class 1) or Restricted/Novice (Class 2).

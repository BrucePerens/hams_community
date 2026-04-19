# Australia Amateur Radio Operator Database

## Important Notice on ACMA RRL
Historically, the Australian Communications and Media Authority (ACMA) provided a bulk download of the Register of Radiocommunications Licences (RRL) which contained all amateur radio operators. However, **due to privacy laws**, individual amateur radio operators have been completely removed from the bulk RRL downloads (only repeaters and club stations remain in the `spectra_rrl.zip` dump).

To fulfill the ethical requirement of verifying operator licenses before granting transmitter access, a secondary source must be used.

## Source Information (Secondary Aggregator)
Since ACMA removed the bulk public data for individuals, developers rely on community-maintained databases or scraping services that preserve or compile the available data.
- **Aggregator Example:** `vklookup.info` or `lokcon.me/vklookup/`
- **Data Completeness:** Because ACMA actively restricts bulk harvesting, any secondary source may be incomplete, out of date, or require interactive queries rather than offering a bulk CSV.

## Download / Verification Process
There is no longer a single, unrestricted "bulk CSV" for Australia that provides individual amateur operator details natively from the ACMA.

To verify a license, the daemon must perform a point-in-time check.
**Primary ACMA Interactive Form (Difficult to scrape):**
https://www.acma.gov.au/register-radiocommunications-licences-rrl

**Community APIs (Easier but unofficial):**
Currently, community tools like `vklookup.info` use backend APIs or static JSON structures compiled over time.
If an API is available, the daemon should perform a GET request:
`GET https://vklookup.info/api/search?callsign={callsign}` *(Note: Verify exact API endpoint of the aggregator)*

### Data Schema (Expected fields from queries)
When querying an Australian callsign, expect to find:
- **Callsign:** e.g., VK3FUR
- **Name:** (If not suppressed by privacy requests)
- **License Class:** Advanced, Standard, or Foundation
- **State/Postcode:** State or territory of the operator.

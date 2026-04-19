# Japan Amateur Radio Operator Database

## Source Information
- **Agency:** Ministry of Internal Affairs and Communications (MIC)
- **Primary Source:** MIC Web-API (無線局等情報検索 - Radio Station Information Search)
- **Aggregator Source:** http://motobayashi.net/callsign/licensesearch.html (Maintained by JJ1WTL)
- **License/Redistribution:** The raw data is from the MIC (Japanese government public data). The aggregator (Motobayashi) provides periodic CSV dumps freely for the amateur radio community.

## Download Process
While the MIC provides an API, it is complex to query in bulk for all ~350,000 operators. The amateur radio community in Japan relies heavily on the parsed CSV dumps provided by JJ1WTL (Motobayashi), which are generated annually from the MIC database.

The daemon can scrape the main Motobayashi page to find the link to the most recent CSV and download it. No firewalls or user-agent spoofing are required.

```bash
# 1. Fetch the main page to find the latest CSV link
curl -s "http://motobayashi.net/callsign/licensesearch.html" | grep -i "\.csv"

# 2. Download the CSV (example URL from 2024)
wget "http://motobayashi.net/callbook/ever/20240828/offline-callbook-ja-20240828-en.csv"
```

## Data Completeness (Validation)
**Test Download Results:** Successfully downloaded the bulk CSV.
- **Records Count:** ~353,455 records (as of the 2024 snapshot).
- **Completeness:** Excellent. This accurately reflects the very high density of amateur radio operators in Japan.

## Data Format & Schema
The data is provided as a clean, comma-separated values (CSV) file with English headers.

**Columns include:**
- `Call`: The Amateur Radio Callsign
- `JCC#/JCG#`: Japan City Code / Japan County Code
- `Prefecture`
- `City/Gun`
- `Ward/Town/Village`
- `Licensed/Renewed Date`
- `License class and Fixed/Mobile` (e.g., 1AM means 1st Class Amateur Mobile)
- `JARL Membersip`: Indicates if they are a JARL member (useful for QSL card routing via the bureau).
- `Licensee`: The name of the licensee.

**Privacy Note:**
Due to Japanese Personal Information Protection Laws, the MIC *does not* disclose the names or street addresses of individual operators. The `Licensee` column is only populated for **Club Stations**. For individual operators, you will only get the callsign, class, and city/prefecture level location.

### Example Data Row
```csv
Call,JCC#/JCG#,Prefecture,City/Gun,AJA#/Hamlog#,Ward/Town/Village,Licensed/Renewed Date (5-year valid),License class and Fixed/Mobile,#th Station under the same Call,JARL Membersip,Buro unavailability,Licensee
JA1BF,1101,Kanagawa,Yokohama,110106,Hodogaya,2022-01-14,1AM,1,JARL,,,
```

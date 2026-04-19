# Amateur Radio Operator Databases Status

This document tracks the status of discovering and documenting amateur radio operator databases for different nations.

| Country | Status | Source Type | Reliable Database? | Provides Name? | Provides Address? | File Path | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Canada | Documented | ZIP (Fixed-width text) | Yes | Yes | Yes | `docs/callbook/Canada.md` | Downloaded ~91k records successfully. Easy direct download via ISED. |
| United Kingdom | Documented | CSV | Yes | Partial (Opt-in) | Partial (Opt-in) | `docs/callbook/UK.md` | Protected by Cloudflare CDN challenge. Requires headless browser. GDPR omissions common. |
| Australia | Documented | Point-in-time API/Scraping | No (ACMA removed individuals) | Partial | Partial | `docs/callbook/Australia.md` | ACMA removed individuals from bulk RRL. Requires checking via third-party (e.g., vklookup). |
| Germany | Documented | PDF | Yes | Partial (Opt-in) | Partial (Opt-in) | `docs/callbook/Germany.md` | Downloadable as PDF. Requires PDF parsing (`pdfplumber`). GDPR omissions common. |
| Japan | Documented | CSV | Yes (via Aggregator) | No (Club only) | No | `docs/callbook/Japan.md` | Downloaded ~353k records successfully. Aggregated annually by JJ1WTL from MIC data. Names/Addresses omitted due to privacy laws. |
| Brazil | Documented | CSV (via Open Data) | Yes | Yes | Partial (City/State) | `docs/callbook/Brazil.md` | Cloudfront protected (401 Unauthorized via curl). Requires headless browser. |
| Argentina | Documented | Web Scraping (PHP form) | Yes | Yes | Partial (City/State) | `docs/callbook/Argentina.md` | Interactive search portal. Requires bypassing SSL validation (`-k`) and HTML parsing. |
| France | Documented | CSV (via API) | Yes | No | Partial (Region) | `docs/callbook/France.md` | Direct download via OpenDataSoft API. Names/Addresses omitted due to GDPR. |
| South Africa | Documented | Web Scraping / API | No bulk data (Scraping only) | Yes | No | `docs/callbook/SouthAfrica.md` | No bulk CSV available. Requires point-in-time scraping of SARL or fallback to HamQTH. |
| New Zealand | Documented | Web Scraping / API | No bulk data (Requires Login) | Yes | Partial | `docs/callbook/NewZealand.md` | Bulk CSV export restricted to logged-in users. Public search page must be queried per callsign. |
| Netherlands | Documented | None (Privacy Restricted) | No public DB | No | No | `docs/callbook/Netherlands.md` | RDI does not publish a public registry. Verification requires international aggregators. |
| Ireland | Documented | None (Privacy Restricted) | No public DB | No | No | `docs/callbook/Ireland.md` | ComReg does not publish a public registry. Verification requires international aggregators. |
| South Korea | Documented | None (Privacy Restricted) | No public DB | No | No | `docs/callbook/SouthKorea.md` | KCA does not publish a public registry. Verification requires international aggregators. |
| Italy | Documented | None (Privacy Restricted) | No public DB | No | No | `docs/callbook/Italy.md` | MIMIT does not publish a public registry due to GDPR. Verification requires international aggregators. |
| Mexico | Documented | None (Privacy Restricted) | No public DB | No | No | `docs/callbook/Mexico.md` | IFT does not publish a public registry. Verification requires international aggregators. |
| Global Fallback | Documented | API / Manual | Varies | Varies | Varies | `docs/callbook/Global_Fallback_Strategy.md` | Defines the 3-Tier strategy (National Data -> Aggregator APIs -> Manual Document Upload). |

# United Kingdom Amateur Radio Operator Database

## Source Information
- **Agency:** Ofcom (Office of Communications)
- **Source URL:** Usually listed under the [Ofcom Open Data page](https://www.ofcom.org.uk/about-ofcom/our-research/opendata) or via direct Freedom of Information (FOI) responses. E.g., `https://www.ofcom.org.uk/siteassets/resources/documents/manage-your-licence/amateur/amateur-callsigns-11-nov-2025.csv`
- **Information Page:** https://www.ofcom.org.uk/about-ofcom/our-research/opendata
- **License/Redistribution:** Open Government Licence v3.0 (OGL), which permits unrestricted use and redistribution provided the source is acknowledged.

## Challenges & Firewalls
The primary domain (`www.ofcom.org.uk`) uses **Cloudflare**, which actively challenges programmatic requests with a `403 Forbidden` response and anti-bot checks (e.g., `cf-mitigated: challenge`).
Standard HTTP requests using `curl` or `requests` even with a spoofed User-Agent will fail against this CDN firewall.

## Suggested Download Process
To bypass the Cloudflare challenge autonomously, the implementing daemon will likely need to use a headless browser with stealth capabilities.

### Headless Browser Approach (e.g., Playwright / Puppeteer)
1. Use a library like `playwright` with `playwright-stealth` or `undetected-chromedriver`.
2. Navigate to the Ofcom Open Data page or the direct CSV URL.
3. Allow the Cloudflare JavaScript challenge to resolve naturally (may take 5-10 seconds).
4. Extract the CSV content or download the file once the challenge passes.

```python
# Conceptual Example using Playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Might need headless=False depending on CF strictness
    context = browser.new_context(user_agent="Mozilla/5.0 ...")
    page = context.new_page()
    page.goto("https://www.ofcom.org.uk/about-ofcom/our-research/opendata")
    # Wait for challenge to pass and locate the download link for the CSV
    # page.click("text=Amateur Radio Callsigns")
```

## Data Format & Schema
Based on historical FOI releases, the data is a standard CSV file.

**Expected Columns:**
- Call Sign
- Class (e.g., Foundation, Intermediate, Full)
- Status (e.g., Allocated, Available)

*Note: Due to GDPR, personal details like names and exact addresses are often omitted in the bulk CSV unless explicitly consented to by the operator.*

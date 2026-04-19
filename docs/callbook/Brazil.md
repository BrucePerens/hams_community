# Brazil Amateur Radio Operator Database

## Source Information
- **Agency:** Agência Nacional de Telecomunicações (Anatel)
- **Database Name:** Outorga e Licenciamento - Estações do Serviço Radioamador (Portal Brasileiro de Dados Abertos)
- **Source URL:** https://dados.gov.br/dataset/estacoes-licenciadas-no-servico-de-radioamador
- **License/Redistribution:** Brazilian Open Data (Dados Abertos), generally unrestricted public data.

## Challenges & Firewalls
The Brazilian government open data portal (`dados.gov.br`) is currently protected by Cloudfront/WAF rules that return `401 Unauthorized` or Cloudfront errors when accessed via standard command-line tools like `curl` or `wget`.
It requires cookies/session tokens (`AWSALB`, `AWSALBCORS`, `SESSION`) and a valid browser fingerprint to access the download links.


### Bot Compliance
Per [ADR-0080](../adrs/0080_good_bot_compliance_and_scraping_ethics.md), our automated agents must adhere to the Dual-Mode Bot Architecture. Since Cloudfront protects this source and may block standard requests, we are authorized to use Exception Mode (e.g., headless browsers, proxy rotation) to fulfill our compliance requirements, assuming good-faith efforts to register as a 'Good Bot' are unviable.
## Suggested Download Process
To automate this download, the daemon must use a headless browser to bypass the Cloudfront protection and extract the actual download link for the CSV file.

### Headless Browser Approach (e.g., Playwright)
1. Use `playwright` (with stealth plugins if necessary) to navigate to the dataset page.
2. The dataset page contains links to resources (Recursos) which point to the actual CSV file.
3. Once the page loads and Cloudfront sets the required cookies, find the download link for the resource named `Estações Licenciadas no Serviço de Radioamador` (usually a CSV inside a ZIP, or a direct CSV link).
4. Download the file using the established browser context.

```python
# Conceptual Example using Playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 ...")
    page = context.new_page()
    page.goto("https://dados.gov.br/dataset/estacoes-licenciadas-no-servico-de-radioamador")
    
    # Locate the resource download link
    # Download the file using page.expect_download()
```

## Data Format & Schema
Based on Anatel's standard Open Data format, the file will be a CSV (often compressed in a ZIP).

**Expected Columns (based on standard Anatel Outorga data):**
- `Indicativo_Prefixo` / `Callsign` (The amateur radio callsign, e.g., PY...)
- `Nome_Entidade` (Name of the operator)
- `Classe` (A, B, or C)
- `Municipio` (City)
- `UF` (State)
- `Status` (Active/Inactive)

The data uses `;` as a delimiter in many Brazilian datasets, and is usually encoded in ISO-8859-1 or UTF-8.

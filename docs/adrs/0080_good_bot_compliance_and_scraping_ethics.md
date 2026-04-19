# ADR 0080: Good Bot Compliance and Scraping Ethics

## Status
Proposed

## Context
Our system operates automated agents that fetch external resources for various purposes. A critical function of our platform is verifying that users are licensed amateur radio operators ("hams"). To achieve this, we must query data from licensing authorities (such as the FCC) and other related databases.

Increasingly, websites use advanced Bot Management solutions (e.g., Cloudflare, Akamai, Fastly) to block automated traffic. If our bots are blocked, we cannot perform mandatory compliance checks, severely degrading our service.

We need a standardized approach to identifying ourselves to the internet. We must behave as a "Good Bot" whenever possible, registering with major CDNs to ensure uninterrupted access. However, some licensing authorities use aggressive bot protection that indiscriminately blocks all automated traffic, including legitimate compliance scrapers. In these specific edge cases, we may be forced to employ evasive ("Bad Bot") techniques to fulfill our legal/compliance obligations.

## Decision

We adopt a **Dual-Mode Bot Architecture**:

### 1. Default Mode: The "Good Bot" Standard
By default, all outgoing automated requests MUST conform to industry "Good Bot" standards. This ensures we are not blocked by generic WAF rules and can participate in CDN allowlisting programs.

**Core Requirements:**
*   **Descriptive User-Agent:** All requests must use a custom, descriptive `User-Agent` string (e.g., `MyProjectBot/1.0 (+https://example.com/bot-info)`). Generic user agents (like `python-requests` or `curl`) are strictly prohibited.
*   **Reverse DNS (PTR):** All egress IP addresses used by our bots MUST have a valid Reverse DNS (PTR) record that resolves to a domain we control. The forward DNS (A/AAAA) for that domain must resolve back to the IP address (Forward-confirmed reverse DNS - FCrDNS).
*   **Robots.txt Compliance:** Crawlers must parse and respect `robots.txt` directives (Allow, Disallow, Crawl-delay).
*   **Rate Limiting:** Aggressive rate limiting must be implemented to avoid overwhelming target servers.

**CDN Registration Programs:**
To guarantee access to sites protected by major CDNs, we will actively participate in their verified bot programs:

*   **Cloudflare Web Bot Auth (Verified Bots):** We will implement HTTP Message Signatures (IETF draft standard).
    1.  Generate an Ed25519 private/public key pair.
    2.  Host a Key Directory (`/.well-known/http-message-signatures-directory`) serving a JSON Web Key Set (JWKS).
    3.  Register our bot and key directory with Cloudflare.
    4.  Sign our outbound HTTP requests to Cloudflare-protected sites using the `Signature`, `Signature-Input`, and `Signature-Agent` headers.
*   **Cloudflare Signed Agents:** For endpoints like AI crawlers or specific monitoring tools, we will register via the Cloudflare dashboard to become a Signed Agent, which relies on similar cryptographic verification or standard identification.
*   **Akamai Validated Bots:** Akamai validates known bots primarily through IP allowlists, Reverse DNS (FCrDNS), and User-Agent matching. We will maintain a public IP list and ensure FCrDNS is perfectly configured so Akamai customers can easily classify us as a "Good Bot."

### 2. Exception Mode: The Compliance Scraper ("Bad Bot" Tactics)
When scraping official licensing authorities (e.g., to verify a ham radio license) where the target site aggressively blocks all bots without offering a verification program, we authorize the use of evasive techniques.

**Authorized "Bad Bot" Techniques (Strictly Limited Scope):**
*   **Browser Spoofing:** Using standard consumer browser `User-Agent` strings.
*   **Headless Browsers:** Utilizing tools like Puppeteer, Playwright, or Selenium to execute JavaScript and pass JS-based challenges (e.g., Cloudflare Turnstile, reCAPTCHA).
*   **IP Rotation / Proxies:** Using proxy networks to distribute requests and avoid IP-based rate limits or bans imposed by the licensing authority.

**Governance:**
"Bad Bot" techniques MAY ONLY be used against specific, documented domains required for compliance verification. Using these techniques against general internet targets is prohibited.

## Consequences
*   **Engineering Overhead:** Implementing Cloudflare Web Bot Auth requires managing cryptographic keys and signing HTTP requests, adding complexity to our HTTP client wrappers.
*   **Infrastructure Requirements:** We must maintain static egress IPs and configure Reverse DNS with our hosting provider.
*   **Uninterrupted Access:** Conforming to good bot standards ensures reliable data ingestion from cooperative sites.
*   **Compliance Guaranteed:** Authorizing evasive techniques as a fallback guarantees we can always verify user licenses, satisfying our core operational requirement.

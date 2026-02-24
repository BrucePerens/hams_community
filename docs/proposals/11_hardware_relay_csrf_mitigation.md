# Proposal 11: Hardware Relay CSRF Mitigation

## 1. Architectural Context
The current local hardware relay (`hams_local_relay.py`) executes QSY (frequency change) commands via standard HTTP GET requests. While Flask-CORS is configured to restrict cross-origin reads, CORS does not prevent a browser from *executing* a simple GET request (e.g., via an `<img>` tag or a form submission on a malicious site).

If an operator with the relay running visits a malicious site, that site can blindly send `http://127.0.0.1:8089/qsy?freq=28.000`. The browser will execute the request and tune the physical radio without the operator's knowledge.

## 2. Integration Design

### A. Local Relay Hardening
**Targets:** `daemons/hams_local_relay/hams_local_relay.py` & `tools/build_relay_packages.py`
* **The Fix:** The relay must explicitly reject any request that does not contain a custom HTTP header (e.g., `X-Hams-Action: execute`). 
* **The Mechanism:** Browsers mandate a CORS Preflight (`OPTIONS`) request before sending custom headers across origins. Because the relay's CORS policy strictly allows `hams.com`, the browser will reject the preflight from a malicious domain and completely block the subsequent GET request.

### B. Web Shack Frontend Updates
**Targets:** `ham_shack/static/src/js/web_shack.js`
* **The Fix:** The `executeQSY` function must be updated to inject the `X-Hams-Action` header into its `fetch()` payload to successfully pass the new relay gateway.

## 3. BDD Acceptance Criteria
* **Story:** As a security architect, I want the local relay to ignore simple GET requests so that malicious websites cannot hijack physical transceivers.
    * *Given* a request to `/qsy` missing the `X-Hams-Action` header
    * *When* intercepted by the Flask / BaseHTTP handler
    * *Then* it MUST return a 403 Forbidden without executing Hamlib commands.

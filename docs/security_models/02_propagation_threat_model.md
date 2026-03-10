# Threat Model: Live Propagation Forecasting Maps

**Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
**Boundary:** `ham_propagation` API and Mathematical Engine

## 1. Spoofing
* **Threat:** A user modifies the API payload to request propagation forecasts for an arbitrary grid square they do not reside in, attempting to bypass geographic restrictions.
* **Mitigation:** The `/api/v1/ham_propagation/muf` endpoint ignores client-supplied grid squares for authenticated users, pulling the grid square strictly from `request.env.user.grid_square` server-side.

## 2. Tampering
* **Threat:** An attacker intercepts the API response to alter the MUF paths, causing operators to target closed bands.
* **Mitigation:** All API traffic is strictly enforced over TLS 1.3. The underlying `ham.space.weather` telemetry is fetched via a secure cron job utilizing cryptographic checksums before database mutations occur.

## 3. Repudiation
* **Threat:** An actor exhausts the VOACAP mathematical engine limits and denies the activity.
* **Mitigation:** API requests are logged via Odoo's standard HTTP routing logger, linking the specific `res.users` ID to the computational request timestamp.

## 4. Information Disclosure (Location Scraping)
* **Threat:** A malicious actor attempts to reverse-engineer propagation polygons to triangulate the exact physical address of radio operators.
* **Mitigation:** The `/api/v1/ham_propagation/muf` endpoint returns data strictly bound to the authenticated user's own session. Because this propagation map is private to the requesting operator, the API safely utilizes their precise, un-fuzzed Maidenhead Grid Square to maximize forecast accuracy. Third parties cannot query this endpoint on behalf of other users, neutralizing the scraping vector.

## 5. Denial of Service (Computational Exhaustion)
* **Threat:** A botnet continuously requests new MUF calculations, exhausting WSGI worker CPU threads.
* **Mitigation:** The calculation results are cached in Redis using `@tools.ormcache` or an explicit Redis setter for 15 minutes per grid-square, completely bypassing the calculation engine for duplicate regional requests.

## 6. Elevation of Privilege
* **Threat:** A vulnerability in the propagation engine allows an attacker to escalate privileges to system admin.
* **Mitigation:** The API controller adheres to the Zero-Sudo architecture. Fetching the space weather telemetry utilizes the `space_weather_service` account context (`.with_user()`). No raw `.sudo()` calls are permitted within the module.

# Proposal 16: Frictionless QRZ Verification

## 1. Architectural Context
The QRZ.com fallback verification requires operators to copy a token, open a new tab, navigate to QRZ, edit their bio, save, return to the platform, and manually click "Verify". This multi-step, multi-tab flow causes high abandonment rates.

## 2. Integration Design
**Targets:** `ham_onboarding/views/verification_templates.xml`, `ham_onboarding/controllers/verification.py`
* **One-Click Clipboard:** Introduce a button that uses the `navigator.clipboard` API to silently copy the `HAMS-XXXXXX` token and displays a temporary "Copied!" tooltip.
* **Deep Linking:** The same button opens a new window directly to `https://www.qrz.com/manager?callsign=XYZ` (using their registered callsign) to skip the QRZ navigation steps.
* **AJAX Auto-Polling:** The verification page initiates a background JavaScript `setInterval`. It polls a new lightweight `/api/v1/onboarding/qrz/status` endpoint every 5 seconds. When the backend detects the token on QRZ, the frontend automatically redirects to the success page without requiring the user to manually click anything.

## 3. BDD Acceptance Criteria
* **Story:** As a user, I want the system to detect when I've updated my QRZ profile automatically.
    * *Given* the QRZ verification page is open
    * *When* the backend scraper successfully finds the token
    * *Then* the frontend AJAX poller MUST detect the state change and automatically redirect the browser to the success dashboard.

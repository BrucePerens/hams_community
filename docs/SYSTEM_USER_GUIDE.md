# Hams.com System User Guide

Welcome to the comprehensive User Guide for the Hams.com platform. This document outlines every feature available to operators through the web interface. 

*Note: For programmatic access and API integration, please see the **[System API Directory](SYSTEM_APIs.md)**.* 

---

## 1. Account Creation & Identity Verification

Because Hams.com provides regulatory tools, verified marketplace access, and public callsign routing, users must verify their identity using the **[Onboarding Engine](/knowledge/home?search=Ham+Identity+&+Onboarding+Manual)**:

* **ARRL LoTW mTLS:** The most seamless method. If you have your `.p12` certificate installed in your browser, accessing the system will automatically complete the onboarding process without requiring passwords.
* **Knowledge Verification (USA Only):** Answer a short technical question pulled directly from the official FCC examination pool.
* **Morse Code Challenge:** An optional challenge for licensed operators who know Morse code. You can verify ownership by manually tapping out your callsign using your spacebar. The system dynamically adapts to your transmission speed (5 to 40 WPM).
* **Official Email OTP:** The system queries the Callbook Directory and sends a One-Time Password to the official email address on file for your callsign.
* **QRZ.com Token:** Generate a unique `HAMS-XXXXXX` token in your account settings, place it in your QRZ.com biography, and click "Verify".
* **Manual ID Submission:** If none of the automated methods work, you can securely upload a photo of your official Amateur Radio license for an administrator to review and approve.

---

## 2. Managing Your Profile & Privacy Settings

All user preferences are centralized in the **Account Settings** hub (`/my/settings`).

**Available Tabs:**
* **Profile:** View your locked regulatory information. Callsign changes must be processed by regulatory sync, not manual editing.
* **Privacy & Security:** 
    * *Directory Masking:* By default, your street address is masked from the public Callbook. You may explicitly opt-in to show your full address.
    * *Geographic Fuzzing:* Control how your station appears on the Community Map. Select "Regional" to mathematically snap your map pin to the center of a 70x100 mile grid box, or "Precise" to use your exact 6-character Maidenhead locator.
* **API Integration:** Generate your private API secret used to connect desktop loggers to the Live REST APIs and the DX Firehose.
* **Automated QSL Sync:** Securely enter your LoTW or eQSL passwords. The platform will gently poll these services once a day to automatically confirm your logbook entries.

---

## 3. Your Personal Website

Every registered user is provisioned a personal subspace (e.g., `hams.com/k6bp`) using the User Websites module. You can drag and drop specialized widgets like the Live DX Cluster, Community Maps, and Morse Code Keys onto your page.

---

## 4. The Ham Radio Logbook

The platform includes a robust, ADIF 3.1.x compliant Logbook. Your contacts are published automatically to your personal URL at `/{your_slug}/logbook`.

**Features:**
* **Cross-Indexing & Confirmations:** The system automatically cross-indexes logs. If you log a contact, and the other station logs the exact same contact (within 15 minutes and 50kHz), the system automatically flags it as **Platform Confirmed**. 
* **Visual Badges:** Unconfirmed contacts appear in <span style="color:red">Red</span>. Confirmed contacts (via the platform, LoTW, or eQSL) appear in <span style="color:green">Green</span>.
* **Nudging:** You can click on any unconfirmed DX callsign in your logbook to view its details. From there, you can click **"Send Nudge Email"** to have the system securely route a polite request asking the operator to upload their log to Hams.com.
* **Space Weather:** SFI, A-Index, and K-Index metrics are automatically injected into your log at the exact time of the contact by the background NOAA Daemon.

---

## 5. Contests & Events

The platform provides a comprehensive contest and event tracking system.
* **Live Net Roster:** A real-time, websocket-powered check-in roster for Net Control Stations (NCS).
* **Claimed vs. Confirmed Scoring:** When calculating contest leaderboards, the system intelligently splits your score. It displays your **Claimed Score** (total contacts logged) alongside your **Confirmed Score** (contacts that have been mathematically verified by the other station or via LoTW/eQSL).

---

## 6. The Callbook Directory & Classifieds

The Callbook is a centralized regulatory directory synchronized daily with the FCC and ISED Canada. It powers the Identity Verification engine, which in turn secures the **Classifieds Marketplace**. Only users who have passed Identity Verification are permitted to create listings or initiate purchases, ensuring a high-trust trading environment.

---

## 7. Web Shack Operating Console

The Web Shack is a highly interactive operating console available at `/shack`. It features smart auto-fill with instant QSO history context, a real-time WebSocket bandmap highlighting needed multipliers, and seamless physical radio tuning via the local hardware relay daemon.

---

## 8. Amateur Satellite Tracking

The platform includes a real-time satellite pass predictor available at `/satellite/tracker`.

For detailed documentation, see the **[Amateur Satellite Tracking Manual](/knowledge/home?search=Amateur+Satellite+Tracking+Manual)**.

**Features:**
* **Live Tracking:** Displays satellites currently above the horizon and calculates upcoming passes in real-time.
* **Location Integration:** Automatically uses your profile's grid square or exact coordinates. You can also manually enter Grid Squares, Decimal Degrees, or Degrees/Minutes/Seconds.
* **Pass Details:** Provides precise Acquisition of Signal (AOS), Time of Closest Approach (TCA), and Loss of Signal (LOS) times and azimuths using ephemeris data synced directly from AMSAT.

## 9. Elmering (Mentorship) Forums

The platform provides a high-trust Q&A environment for experienced operators to mentor new hams (`/forum`).
For detailed documentation, see the **[Elmering Forums Manual](../ham_forum_extension/data/documentation.html)**.

**Features:**
* **Zero-Sudo Moderation:** Community moderation operates seamlessly without requiring full system admin privileges.
* **Dynamic Trust Badges:** Forum posts display the user's license class (e.g., "Amateur Extra" or "Prospective Ham (SWL)") and an identity verification badge to establish authority.
* **Spam Prevention:** Authenticated users bypass CAPTCHAs, relying on the platform's robust onboarding gatekeeper to maintain a spam-free environment.

## 10. Live Propagation Forecasting

Available at `/propagation`, this tool provides real-time High Frequency (HF) band condition mapping.
For detailed documentation, see the **[Live Propagation Forecasting Manual](../ham_propagation/data/documentation.html)**.

**Features:**
* **MUF Heatmaps:** Displays a visual map of reachable geographic regions (Maximum Usable Frequency paths) based on the latest NOAA space weather metrics and your unworked DXCC goals.
* **Accessibility:** Includes a WCAG 2.1 AA compliant text-based tabular summary of open and closed bands for visually impaired operators.

## 11. Morse Code Academy & Exam Prep

The platform provides a comprehensive environment to study for your license and learn Morse Code (CW).

**Features:**
* **Spaced Repetition Exams:** Practice exams dynamically prioritize questions you have previously struggled with.
* **In-Depth Explanations:** Review screens provide detailed breakdowns of why specific answers are correct or incorrect.
* **Morse Code Progression:** An integrated Koch method trainer tracks your proficiency, unlocking new characters automatically as your speed increases up to 100 WPM using Farnsworth timing.

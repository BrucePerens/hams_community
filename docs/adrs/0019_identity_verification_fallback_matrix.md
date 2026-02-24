# ADR 0019: Identity Verification Fallback Matrix

## Status
Accepted

## Context
The platform must reliably verify the identity of amateur radio operators to grant them high-trust access to features like the peer-to-peer Classifieds. However, the global amateur radio community is incredibly diverse, and relying on a single verification method leads to severe accessibility and internationalization barriers. For example:
* The **Ham-CAPTCHA** relies entirely on the United States FCC (NCVEC) question pools, making it difficult or impossible for international hams to pass without studying foreign regulations.
* Not all operators use **ARRL Logbook of the World (LoTW)** or possess digital `.p12` certificates.
* Not all operators know **Morse Code**.
* The **Official Email OTP** relies on us having their email on file, which depends on their country's regulatory database providing public email addresses (like the FCC ULS).

## Decision
To ensure the platform remains secure against scammers while remaining universally accessible to legitimate operators worldwide, we implement a structured **Identity Verification Fallback Matrix**.

The system must support and present the following hierarchical paths to the user:

1. **Cryptographic (The Golden Path):** ARRL LoTW mTLS Certificate. Highly trusted, instantaneous, and international.
2. **Knowledge/Procedural (Primary Fallback):** 
   * **US-Based:** Ham-CAPTCHA (NCVEC question pool).
   * **Global:** QRZ.com profile token scraping.
3. **Skill-Based (Secondary Fallback):** Morse Code Transmission Challenge. A universally recognized amateur radio skill. Users manually tap out their callsign, and a dynamic JS clustering algorithm decodes it, adapting to any speed between 5 and 40 WPM.
4. **Regulatory (Tertiary Fallback):** Official Email OTP routed to the address published by their federal telecommunications authority.
5. **Manual Verification (The Ultimate Fallback):** If all automated methods fail or are inapplicable, users can securely upload a photo of their physical Amateur Radio license. This generates an action item for human administrators to review and approve the account.

## Consequences
* **Positive:** Maximizes global user adoption by guaranteeing that every legitimate operator on Earth has at least one viable path to become a trusted, verified user, without lowering the security barrier against automated spam bots.
* **Negative:** The manual ID fallback introduces unavoidable administrative overhead and onboarding friction (wait times) for users who are forced to the bottom of the matrix.

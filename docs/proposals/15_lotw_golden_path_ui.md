# Proposal 15: The "Golden Path" LoTW UI Overhaul

## 1. Architectural Context
The current LoTW mTLS onboarding requires users to export a P12 certificate and import it into their browser's keychain. Browsers deliberately hide these settings for security reasons, making the process highly intimidating for non-technical operators who are met with a massive wall of text.

## 2. Integration Design
**Targets:** `ham_onboarding/views/signup_templates.xml`, `ham_onboarding/static/src/js/...`
* **OS-Aware Guides:** Utilize `navigator.userAgent` on the frontend to detect the operating system (Windows, macOS, Linux, iOS, Android) and dynamically render only the relevant set of instructions.
* **Visual Walkthrough:** Replace text walls with a 3-step carousel containing 5-second looping GIFs showing the exact UI clicks required in TQSL and the target OS's certificate manager.
* **Failsafe Escape Hatch:** Add a prominent "I'll do this later" button that cleanly exits the mTLS flow and drops the user into the standard Ham-CAPTCHA / QRZ fallback flow without losing their momentum.

## 3. BDD Acceptance Criteria
* **Story:** As a non-technical user, I want visual guidance tailored to my computer so I don't get lost in browser settings.
    * *Given* a user accessing the LoTW Help page on macOS
    * *When* the page renders
    * *Then* it MUST default to the Apple Keychain visual guide and actively hide the Windows Certificate Manager guide.

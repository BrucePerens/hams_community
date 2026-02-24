# Runbook: Security & Compliance Paradigms

This document details the architectural rules enforced across the application to maintain data integrity and regulatory alignment.

## 1. The Service Account Pattern (Zero-Sudo Architecture)
*(Reference: ham_base/models/security_utils.py -> _get_service_uid -> [%ANCHOR: get_service_uid])*
Developers are strictly prohibited from utilizing the raw `.sudo()` method to bypass access control lists. Whenever a low-privilege actor must execute a restricted action (e.g., modifying DNS zone files), the logic must:
1. Identify the designated internal service account XML ID.
2. Retrieve the account's database ID via the centralized security utility.
3. Apply the `with_user()` context manager to impersonate that specific service account, ensuring the operation remains bound by explicit Record Rules.

## 2. GDPR Data Portability & Erasure
*(Reference: ham_onboarding/models/res_users.py -> _execute_gdpr_erasure)*
All modules storing personally identifiable information must extend the central privacy hooks on the user model. This ensures that users can extract a complete JSON representation of their data and permanently destroy their account profile upon request.

## 3. Public RF Record Exemptions
*(Reference: ham_logbook/models/ham_qso.py)*
Because amateur radio transmissions occur over public frequencies, logged contacts are treated as public historical records. When an operator invokes their right to erasure, their account is destroyed, but the relational links on their logbook entries use the `ondelete='set null'` constraint. This anonymizes the records without corrupting the platform's cryptographic confirmation network.

## 4. Geographic Fuzzing
*(Reference: ham_callbook/models/ham_callbook.py -> _compute_coordinates -> [%ANCHOR: geographic_fuzzing])*
Unless an operator explicitly configures their profile to broadcast precise location data, the mapping engine intercepts their Maidenhead Grid Square and truncates it. This mathematically forces their map pin to render in the center of a massive regional bounding box, preventing precise address triangulation.

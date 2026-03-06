# Runbook: Security & Compliance Paradigms

This document outlines the security and compliance rules we enforce across the platform.

## 1. The Service Account Pattern (Zero-Sudo Architecture)
*(Reference: zero_sudo/models/security_utils.py -> _get_service_uid)*
Never use the raw `.sudo()` method. When a standard user needs to perform a restricted action (like modifying DNS records), you must:
1. Identify the designated internal service account XML ID.
2. Retrieve the account's database ID via the centralized security utility.
3. Apply the `with_user()` context manager to impersonate that specific service account, ensuring the operation remains bound by explicit Record Rules.

## 2. GDPR Data Portability & Erasure
*(Reference: user_websites/models/res_users.py -> _execute_gdpr_erasure)*
All modules storing personally identifiable information must extend the central privacy hooks on the user model. This ensures that users can extract a complete JSON representation of their data and permanently destroy their account profile upon request.

## 3. Public Record Exemptions
Because certain operations occur in public spaces, logged records can be treated as public historical records. When a user invokes their right to erasure, their account is destroyed, but the relational links on these entries use the `ondelete='set null'` constraint. This anonymizes the records without corrupting the platform's historical data network.

## 4. Geographic Fuzzing
Unless a user explicitly configures their profile to broadcast precise location data, the mapping engine intercepts their coordinates and truncates them. This mathematically forces their map pin to render in the center of a massive regional bounding box, preventing precise address triangulation.
